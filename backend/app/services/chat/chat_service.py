"""
Chat service - Multi-turn conversation with Claude AI using tool_use.

- Uses messages.stream() for real word-by-word streaming
- Stores raw_content for multi-turn history reconstruction
- Persists each intermediate turn (assistant+tool_result) in DB
- DB session managed manually by SSE lifecycle
"""
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional

from anthropic import AsyncAnthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.chat import ChatConversation, ChatMessage
from app.services.ai.client_manager import ai_client_manager
from app.services.chat.tools import CHAT_TOOLS
from app.services.chat.tool_executor import tool_executor

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5
MAX_HISTORY_MESSAGES = 20


class ChatService:
    """Conversational chat service with Claude AI tool_use and real streaming"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_CHAT_MODEL

    def _build_system_prompt(self, client_context: Optional[str] = None) -> str:
        base = """Eres el asistente de MediaFlow, un sistema profesional de audio y radio automatizada.

Tu rol es ayudar al usuario a:
1. Generar textos para anuncios de audio (spots, jingles, avisos)
2. Crear audio TTS con las voces disponibles
3. Guardar audios en la biblioteca
4. Programar audios para reproducción automática
5. Buscar y gestionar audios existentes
6. Enviar audios a la radio

## Comportamiento:
- Responde siempre en español
- Sé conciso y directo
- Cuando el usuario describe lo que quiere anunciar, genera sugerencias de texto primero
- Cuando el usuario elige un texto, pregunta con qué voz quiere el audio (o usa la predeterminada)
- Después de generar un audio, pregunta si quiere guardarlo en biblioteca o programarlo
- Si el usuario pide algo ambiguo, pregunta para clarificar

## Reglas:
- SIEMPRE usa las herramientas disponibles para ejecutar acciones. NO inventes datos.
- Siempre que presentes opciones (sugerencias, voces, música, tonos, etc.), numéralas claramente (1, 2, 3...) para que el usuario pueda responder solo con el número.
- Si el usuario responde con un número, interprétalo como la selección de esa opción.
- Cuando listes voces o música, presenta la información de forma amigable.
- Después de generar un audio, NO repitas los metadatos técnicos (duración, voz, ID). El reproductor ya muestra esa información. Solo confirma brevemente que el audio está listo y pregunta qué quiere hacer.
"""
        if client_context:
            base += f"\n## Contexto del negocio:\n{client_context}\n"
        return base

    async def send_message(
        self,
        user_message: str,
        conversation_id: Optional[int],
        db: AsyncSession,
    ) -> AsyncGenerator[str, None]:
        """
        Process user message and yield SSE events with real streaming.

        Events: message_start, text_delta, tool_start, tool_result,
                audio_generated, message_end, error
        """
        try:
            # 1. Get or create conversation
            conversation = await self._get_or_create_conversation(
                conversation_id, user_message, db
            )
            yield self._sse_event("message_start", {"conversation_id": conversation.id})

            # 2. Save user message
            user_msg = ChatMessage(
                conversation_id=conversation.id,
                role="user", content=user_message, raw_content=user_message,
            )
            db.add(user_msg)
            await db.flush()

            # 3. Build messages history (with full tool_use structure)
            messages = await self._build_messages_history(conversation.id, db)

            # 4. Get AI client context
            active_client = await ai_client_manager.get_active_client(db)
            client_context = active_client.context if active_client else None
            system_prompt = self._build_system_prompt(client_context)

            # 5. Claude conversation loop with REAL STREAMING
            all_tool_calls = []
            iteration = 0

            while iteration < MAX_TOOL_ITERATIONS:
                iteration += 1

                # --- Stream response from Claude ---
                assistant_content_blocks = []
                assistant_text_parts = []
                tool_use_blocks = []
                current_text_index = -1
                current_tool_input_json = ""
                current_tool_name = ""
                current_tool_id = ""

                logger.info(f"Chat stream iteration {iteration} using model: {self.model}")
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=2048,
                    system=system_prompt,
                    tools=CHAT_TOOLS,
                    messages=messages,
                ) as stream:
                    async for event in stream:
                        if event.type == "content_block_start":
                            if event.content_block.type == "text":
                                current_text_index = len(assistant_content_blocks)
                                assistant_content_blocks.append({"type": "text", "text": ""})
                                assistant_text_parts.append("")
                            elif event.content_block.type == "tool_use":
                                current_tool_name = event.content_block.name
                                current_tool_id = event.content_block.id
                                current_tool_input_json = ""
                                yield self._sse_event("tool_start", {"tool": current_tool_name})

                        elif event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                assistant_text_parts[current_text_index] += event.delta.text
                                yield self._sse_event("text_delta", {"text": event.delta.text})
                            elif event.delta.type == "input_json_delta":
                                current_tool_input_json += event.delta.partial_json

                        elif event.type == "content_block_stop":
                            # Use if/elif to avoid processing both text and tool on same stop
                            if current_tool_name:
                                # Finalize tool_use block
                                try:
                                    tool_input = json.loads(current_tool_input_json) if current_tool_input_json else {}
                                except json.JSONDecodeError:
                                    tool_input = {}

                                tool_use_blocks.append({
                                    "id": current_tool_id,
                                    "name": current_tool_name,
                                    "input": tool_input,
                                })
                                assistant_content_blocks.append({
                                    "type": "tool_use",
                                    "id": current_tool_id,
                                    "name": current_tool_name,
                                    "input": tool_input,
                                })
                                current_tool_name = ""
                                current_tool_id = ""
                                current_tool_input_json = ""
                            elif current_text_index >= 0 and current_text_index < len(assistant_content_blocks):
                                # Finalize text block
                                if assistant_content_blocks[current_text_index]["type"] == "text":
                                    assistant_content_blocks[current_text_index]["text"] = assistant_text_parts[current_text_index]

                # Collect full text from this iteration
                iteration_text = "".join(assistant_text_parts)
                logger.info(f"Iteration {iteration} done. Text length: {len(iteration_text)}, tools: {len(tool_use_blocks)}")

                # --- If no tool_use, conversation turn is done ---
                if not tool_use_blocks:
                    assistant_msg = ChatMessage(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=iteration_text,
                        raw_content=assistant_content_blocks if assistant_content_blocks else None,
                    )
                    # Link audio if generated in any iteration
                    for tc in all_tool_calls:
                        if tc["tool"] == "generate_audio" and tc["result"].get("success"):
                            assistant_msg.audio_id = tc["result"]["data"]["audio_id"]
                            break
                    db.add(assistant_msg)
                    logger.info("No tools, breaking loop")
                    break

                # --- Tools were used: persist this intermediate turn ---
                intermediate_assistant = ChatMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=iteration_text,
                    raw_content=assistant_content_blocks,
                )
                db.add(intermediate_assistant)

                # Add to Claude message history
                messages.append({"role": "assistant", "content": assistant_content_blocks})

                # --- Execute tools ---
                tool_results_for_claude = []
                for tool_block in tool_use_blocks:
                    result = await tool_executor.execute(
                        tool_block["name"], tool_block["input"], db
                    )
                    all_tool_calls.append({
                        "tool": tool_block["name"],
                        "tool_use_id": tool_block["id"],
                        "input": tool_block["input"],
                        "result": result,
                    })

                    yield self._sse_event("tool_result", {
                        "tool": tool_block["name"], "result": result,
                    })

                    if tool_block["name"] == "generate_audio" and result.get("success"):
                        yield self._sse_event("audio_generated", result["data"])

                    tool_results_for_claude.append({
                        "type": "tool_result",
                        "tool_use_id": tool_block["id"],
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })

                # Save tool_result message to DB
                tool_result_msg = ChatMessage(
                    conversation_id=conversation.id,
                    role="tool_result",
                    content="",
                    raw_content=tool_results_for_claude,
                )
                db.add(tool_result_msg)

                # Add to Claude history for next iteration
                messages.append({"role": "user", "content": tool_results_for_claude})

            logger.info("Committing to DB...")
            await db.commit()
            logger.info("Committed. Sending message_end.")
            yield self._sse_event("message_end", {"conversation_id": conversation.id})

        except Exception as e:
            await db.rollback()
            logger.error(f"Chat error: {e}", exc_info=True)
            yield self._sse_event("error", {"message": str(e)})

    async def _get_or_create_conversation(
        self, conversation_id: Optional[int], first_message: str, db: AsyncSession
    ) -> ChatConversation:
        if conversation_id:
            result = await db.execute(
                select(ChatConversation).filter(ChatConversation.id == conversation_id)
            )
            conv = result.scalar_one_or_none()
            if conv:
                return conv

        title = first_message[:80] + ("..." if len(first_message) > 80 else "")
        conv = ChatConversation(title=title)
        db.add(conv)
        await db.flush()
        return conv

    async def _build_messages_history(self, conversation_id: int, db: AsyncSession) -> List[Dict]:
        """
        Rebuild Claude messages from DB using raw_content.
        Preserves tool_use/tool_result structure for multi-turn context.
        """
        result = await db.execute(
            select(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
        )
        db_messages = result.scalars().all()
        recent = db_messages[-MAX_HISTORY_MESSAGES:] if len(db_messages) > MAX_HISTORY_MESSAGES else db_messages

        messages = []
        for msg in recent:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                if msg.raw_content and isinstance(msg.raw_content, list):
                    messages.append({"role": "assistant", "content": msg.raw_content})
                else:
                    messages.append({"role": "assistant", "content": msg.content})
            elif msg.role == "tool_result":
                if msg.raw_content and isinstance(msg.raw_content, list):
                    messages.append({"role": "user", "content": msg.raw_content})
        return messages

    def _sse_event(self, event_type: str, data: dict) -> str:
        payload = json.dumps({"type": event_type, **data}, ensure_ascii=False, default=str)
        return f"event: {event_type}\ndata: {payload}\n\n"


chat_service = ChatService()
