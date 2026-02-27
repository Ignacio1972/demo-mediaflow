# Chat Assistant - Fase 1: Backend

**Objetivo**: Servicio de chat conversacional con Claude AI + tool_use para ejecutar acciones en MediaFlow (generar audio, guardar, programar, etc.) via SSE streaming.

---

## Arquitectura

```
Cliente (Frontend)
  │
  │ POST /api/v1/chat/send  (SSE stream)
  │ GET  /api/v1/chat/conversations
  │ GET  /api/v1/chat/conversations/:id
  │ DELETE /api/v1/chat/conversations/:id
  │
  ▼
┌─────────────────────────────────────────┐
│  chat.py (endpoint)                     │
│  - Recibe mensaje del usuario           │
│  - Crea session DB manual (NO Depends)  │
│  - Retorna StreamingResponse con SSE    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  ChatService (services/chat/)           │
│  - Usa messages.stream() (STREAMING)    │
│  - Procesa tool_use en loop             │
│  - Ejecuta herramientas reales          │
│  - Yield eventos SSE en tiempo real     │
└────────────────┬────────────────────────┘
                 │
          ┌──────┼──────────┐
          ▼      ▼          ▼
     Claude   ToolExecutor  DB
     API      (acciones)    (historial)
```

---

## Paso 0: Extraer servicio de generación de audio (HACER PRIMERO)

Extraer la lógica de `POST /api/v1/audio/generate` (inline en `audio.py` lineas ~135-301) a un servicio reutilizable.

### Archivo: `backend/app/services/audio/generator.py`

```python
"""
Audio generation service - reusable from both REST endpoints and chat assistant.
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.services.tts.voice_manager import voice_manager
from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_audio_message(
    text: str,
    voice_id: str,
    db: AsyncSession,
    add_jingles: bool = False,
    music_file: Optional[str] = None,
    display_name: Optional[str] = None,
    category_id: Optional[str] = None,
    priority: int = 4,
) -> Dict[str, Any]:
    """
    Generate a TTS audio message and save to database.
    Returns dict with: id, filename, audio_url, duration, display_name, voice_id

    IMPLEMENTAR: Copiar lógica del endpoint POST /api/v1/audio/generate (audio.py).
    Flujo:
    1. Obtener VoiceSettings de la DB por voice_id
    2. voice_manager.generate_with_voice(text, voice_id, db)
       → retorna (audio_bytes, voice_settings_used, effective_settings)
    3. Si add_jingles: jingle_service.create_jingle(audio_bytes, music_file, ...)
    4. Guardar en settings.AUDIO_PATH / filename
    5. Crear AudioMessage en DB
    6. Retornar dict
    """
    raise NotImplementedError("Extraer lógica de audio.py aquí")
```

### Refactorizar endpoint original

```python
# En audio.py, el endpoint POST /generate ahora llama al servicio:
from app.services.audio.generator import generate_audio_message

@router.post("/generate")
async def generate_audio(request: AudioGenerateRequest, db: AsyncSession = Depends(get_db)):
    result = await generate_audio_message(
        text=request.text, voice_id=request.voice_id, db=db,
        add_jingles=request.add_jingles, music_file=request.music_file,
        display_name=request.display_name, category_id=request.category_id,
        priority=request.priority,
    )
    return AudioGenerateResponse(**result)
```

---

## Paso 1: Modelo de Base de Datos

### Archivo: `backend/app/models/chat.py`

```python
"""
Chat conversation and message models.

raw_content guarda la estructura completa de Anthropic (text + tool_use + tool_result)
para reconstruir el historial multi-turno correctamente.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class ChatConversation(Base, TimestampMixin):
    """A chat conversation session"""
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    messages = relationship("ChatMessage", back_populates="conversation",
                          order_by="ChatMessage.created_at",
                          cascade="all, delete-orphan")


class ChatMessage(Base, TimestampMixin):
    """A single message in a conversation"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)

    role = Column(String(20), nullable=False)   # "user" | "assistant" | "tool_result"
    content = Column(Text, nullable=False, default="")  # Texto visible

    # Estructura raw de Anthropic para reconstruir historial con tool_use
    # assistant: [{type:"text",text:"..."}, {type:"tool_use",id:"...",name:"...",input:{}}]
    # tool_result: [{type:"tool_result",tool_use_id:"...",content:"..."}]
    raw_content = Column(JSON, nullable=True)

    audio_id = Column(Integer, ForeignKey("audio_messages.id"), nullable=True)
    audio = relationship("AudioMessage", lazy="joined")

    conversation = relationship("ChatConversation", back_populates="messages")
```

### Registrar y migrar

```python
# En backend/app/models/__init__.py agregar:
from app.models.chat import ChatConversation, ChatMessage
```

```bash
cd /var/www/mediaflow-v2/backend && source venv/bin/activate
alembic revision --autogenerate -m "add chat conversations and messages"
alembic upgrade head
```

---

## Paso 2: Definir Herramientas de Claude

### Archivo: `backend/app/services/chat/tools.py`

```python
"""
Chat assistant tool definitions for Claude tool_use.
"""

CHAT_TOOLS = [
    {
        "name": "generate_text_suggestions",
        "description": "Genera 2-3 sugerencias de texto para un anuncio de audio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "Qué se quiere anunciar"},
                "tone": {
                    "type": "string",
                    "enum": ["profesional", "entusiasta", "amigable", "urgente", "informativo"],
                    "description": "Tono del mensaje"
                },
                "duration": {"type": "integer", "description": "Duración objetivo en segundos (5-30)", "default": 10}
            },
            "required": ["context"]
        }
    },
    {
        "name": "generate_audio",
        "description": "Genera audio TTS a partir de un texto confirmado por el usuario.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a convertir en audio"},
                "voice_id": {"type": "string", "description": "ID de la voz (si no se especifica, usa la default)"},
                "add_jingles": {"type": "boolean", "description": "Si agregar música de fondo", "default": False},
                "music_file": {"type": "string", "description": "Archivo de música de fondo (opcional)"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "list_voices",
        "description": "Lista las voces disponibles para generar audio.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "list_music_tracks",
        "description": "Lista las pistas de música de fondo disponibles.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "save_to_library",
        "description": "Guarda un audio generado en la biblioteca permanente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_id": {"type": "integer", "description": "ID del audio a guardar"},
                "display_name": {"type": "string", "description": "Nombre para la biblioteca (opcional)"},
                "category_id": {"type": "string", "description": "ID de categoría (opcional)"}
            },
            "required": ["audio_id"]
        }
    },
    {
        "name": "create_schedule",
        "description": "Programa un audio para reproducción automática.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_id": {"type": "integer", "description": "ID del audio"},
                "schedule_type": {
                    "type": "string",
                    "enum": ["interval", "specific", "once"],
                    "description": "interval=cada X tiempo, specific=horarios fijos, once=una vez"
                },
                "interval_minutes": {"type": "integer", "description": "Minutos entre repeticiones (tipo interval)"},
                "specific_times": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Horarios HH:MM (tipo specific). Ej: ['09:00', '12:00']"
                },
                "days_of_week": {
                    "type": "array", "items": {"type": "integer"},
                    "description": "Días 0-6 (lunes=0). Para tipo specific."
                },
                "start_date": {"type": "string", "description": "Fecha inicio ISO. Para tipo 'once', es la fecha/hora de ejecución."},
                "end_date": {"type": "string", "description": "Fecha fin ISO (opcional)"}
            },
            "required": ["audio_id", "schedule_type"]
        }
    },
    {
        "name": "list_schedules",
        "description": "Lista las programaciones activas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "active_only": {"type": "boolean", "description": "Solo activas", "default": True}
            },
            "required": []
        }
    },
    {
        "name": "list_categories",
        "description": "Lista las categorías disponibles para organizar audios.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "search_library",
        "description": "Busca audios guardados en la biblioteca.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto de búsqueda"},
                "category_id": {"type": "string", "description": "Filtrar por categoría"},
                "limit": {"type": "integer", "description": "Máximo resultados", "default": 10}
            },
            "required": []
        }
    },
    {
        "name": "send_to_radio",
        "description": "Envía un audio a la radio para reproducción inmediata.",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_id": {"type": "integer", "description": "ID del audio"}
            },
            "required": ["audio_id"]
        }
    }
]
```

---

## Paso 3: Ejecutor de Herramientas

### Archivo: `backend/app/services/chat/tool_executor.py`

```python
"""
Tool executor - executes tools invoked by Claude against MediaFlow services.
"""
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.models.category import Category
from app.services.ai.claude import claude_service
from app.services.ai.client_manager import ai_client_manager
from app.services.audio.generator import generate_audio_message
from app.core.config import settings

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes chat assistant tools against MediaFlow services"""

    async def execute(self, tool_name: str, tool_input: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Execute a tool. Returns {success, data, message}."""
        handler = getattr(self, f"_tool_{tool_name}", None)
        if not handler:
            return {"success": False, "message": f"Herramienta desconocida: {tool_name}"}
        try:
            return await handler(tool_input, db)
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}

    async def _tool_generate_text_suggestions(self, params: Dict, db: AsyncSession) -> Dict:
        active_client = await ai_client_manager.get_active_client(db)
        client_context = active_client.context if active_client else None

        suggestions = await claude_service.generate_announcements(
            context=params["context"],
            tone=params.get("tone", "profesional"),
            duration=params.get("duration", 10),
            client_context=client_context,
        )
        return {
            "success": True,
            "data": suggestions,
            "message": f"Se generaron {len(suggestions)} sugerencias de texto."
        }

    async def _tool_generate_audio(self, params: Dict, db: AsyncSession) -> Dict:
        text = params["text"]
        voice_id = params.get("voice_id")

        # Get default voice if not specified
        if not voice_id:
            result = await db.execute(
                select(VoiceSettings).filter(
                    VoiceSettings.is_default == True, VoiceSettings.active == True
                )
            )
            default_voice = result.scalar_one_or_none()
            if not default_voice:
                result = await db.execute(
                    select(VoiceSettings).filter(VoiceSettings.active == True).limit(1)
                )
                default_voice = result.scalar_one_or_none()
            if not default_voice:
                return {"success": False, "message": "No hay voces configuradas"}
            voice_id = default_voice.id

        audio_result = await generate_audio_message(
            text=text, voice_id=voice_id, db=db,
            add_jingles=params.get("add_jingles", False),
            music_file=params.get("music_file"),
        )
        return {
            "success": True,
            "data": {
                "audio_id": audio_result["id"],
                "filename": audio_result["filename"],
                "audio_url": audio_result["audio_url"],
                "duration": audio_result["duration"],
                "voice_id": voice_id,
            },
            "message": f"Audio generado: {audio_result['duration']:.1f}s con voz {voice_id}"
        }

    async def _tool_list_voices(self, params: Dict, db: AsyncSession) -> Dict:
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.active == True).order_by(VoiceSettings.name)
        )
        voices = result.scalars().all()
        voice_list = [
            {"id": v.id, "name": v.name, "is_default": v.is_default}
            for v in voices
        ]
        return {
            "success": True, "data": voice_list,
            "message": f"Hay {len(voice_list)} voces: {', '.join(v['name'] for v in voice_list)}"
        }

    async def _tool_list_music_tracks(self, params: Dict, db: AsyncSession) -> Dict:
        from app.models.music_track import MusicTrack
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.active == True).order_by(MusicTrack.display_name)
        )
        tracks = result.scalars().all()
        track_list = [
            {"filename": t.filename, "display_name": t.display_name,
             "duration": t.duration, "is_default": t.is_default}
            for t in tracks
        ]
        return {"success": True, "data": track_list,
                "message": f"Hay {len(track_list)} pistas de música disponibles."}

    async def _tool_save_to_library(self, params: Dict, db: AsyncSession) -> Dict:
        audio_id = params["audio_id"]
        result = await db.execute(select(AudioMessage).filter(AudioMessage.id == audio_id))
        audio = result.scalar_one_or_none()
        if not audio:
            return {"success": False, "message": f"Audio #{audio_id} no encontrado"}

        audio.is_favorite = True
        if params.get("display_name"):
            audio.display_name = params["display_name"]
        if params.get("category_id"):
            audio.category_id = params["category_id"]
        await db.flush()

        return {"success": True,
                "data": {"audio_id": audio_id, "display_name": audio.display_name},
                "message": f"Audio '{audio.display_name}' guardado en biblioteca."}

    async def _tool_create_schedule(self, params: Dict, db: AsyncSession) -> Dict:
        from app.models.schedule import Schedule
        from datetime import datetime

        audio_id = params["audio_id"]
        schedule_type = params["schedule_type"]

        result = await db.execute(select(AudioMessage).filter(AudioMessage.id == audio_id))
        audio = result.scalar_one_or_none()
        if not audio:
            return {"success": False, "message": f"Audio #{audio_id} no encontrado"}

        # Para tipo "once", start_date es la fecha/hora de ejecución (no existe once_datetime)
        schedule = Schedule(
            audio_message_id=audio_id,
            schedule_type=schedule_type,
            active=True,
            start_date=datetime.fromisoformat(params["start_date"]) if params.get("start_date") else datetime.now(),
        )

        if params.get("end_date"):
            schedule.end_date = datetime.fromisoformat(params["end_date"])
        if schedule_type == "interval":
            schedule.interval_minutes = params.get("interval_minutes", 60)
        elif schedule_type == "specific":
            schedule.specific_times = params.get("specific_times", [])
            schedule.days_of_week = params.get("days_of_week", [0, 1, 2, 3, 4, 5, 6])

        db.add(schedule)
        await db.flush()

        return {"success": True,
                "data": {"schedule_id": schedule.id, "schedule_type": schedule_type},
                "message": f"Audio '{audio.display_name}' programado ({schedule_type})."}

    async def _tool_list_schedules(self, params: Dict, db: AsyncSession) -> Dict:
        from app.models.schedule import Schedule
        query = select(Schedule)
        if params.get("active_only", True):
            query = query.filter(Schedule.active == True)
        result = await db.execute(query.order_by(Schedule.created_at.desc()).limit(20))
        schedules = result.scalars().all()

        return {"success": True,
                "data": [
                    {"id": s.id, "audio_message_id": s.audio_message_id,
                     "schedule_type": s.schedule_type, "active": s.active,
                     "next_execution_at": s.next_execution_at.isoformat() if s.next_execution_at else None}
                    for s in schedules
                ],
                "message": f"Hay {len(schedules)} programaciones."}

    async def _tool_list_categories(self, params: Dict, db: AsyncSession) -> Dict:
        result = await db.execute(
            select(Category).filter(Category.active == True).order_by(Category.order)
        )
        categories = result.scalars().all()
        cat_list = [{"id": c.id, "name": c.name, "icon": c.icon, "color": c.color} for c in categories]
        return {"success": True, "data": cat_list,
                "message": f"Hay {len(cat_list)} categorías: {', '.join(c['name'] for c in cat_list)}"}

    async def _tool_search_library(self, params: Dict, db: AsyncSession) -> Dict:
        query = select(AudioMessage).filter(
            AudioMessage.is_favorite == True, AudioMessage.status != "deleted"
        )
        if params.get("query"):
            search = f"%{params['query']}%"
            query = query.filter(
                AudioMessage.display_name.ilike(search) | AudioMessage.original_text.ilike(search)
            )
        if params.get("category_id"):
            query = query.filter(AudioMessage.category_id == params["category_id"])

        limit = min(params.get("limit", 10), 20)
        result = await db.execute(query.order_by(AudioMessage.created_at.desc()).limit(limit))
        messages = result.scalars().all()

        return {"success": True,
                "data": [
                    {"id": m.id, "display_name": m.display_name, "duration": m.duration,
                     "voice_id": m.voice_id, "audio_url": f"/storage/audio/{m.filename}",
                     "created_at": m.created_at.isoformat() if m.created_at else None}
                    for m in messages
                ],
                "message": f"Se encontraron {len(messages)} audios."}

    async def _tool_send_to_radio(self, params: Dict, db: AsyncSession) -> Dict:
        audio_id = params["audio_id"]
        result = await db.execute(select(AudioMessage).filter(AudioMessage.id == audio_id))
        audio = result.scalar_one_or_none()
        if not audio:
            return {"success": False, "message": f"Audio #{audio_id} no encontrado"}

        from app.services.azuracast.client import azuracast_client
        radio_result = await azuracast_client.send_audio_to_radio(audio.file_path)

        if radio_result.get("success"):
            audio.sent_to_player = True
            await db.flush()

        return {
            "success": radio_result.get("success", False),
            "data": {"audio_id": audio_id},
            "message": f"Audio '{audio.display_name}' enviado a la radio." if radio_result.get("success") else "Error enviando a la radio."
        }


tool_executor = ToolExecutor()
```

---

## Paso 4: Servicio de Chat (streaming real)

### Archivo: `backend/app/services/chat/chat_service.py`

```python
"""
Chat service - Multi-turn conversation with Claude AI using tool_use.

- Usa messages.stream() para streaming real palabra por palabra
- Guarda raw_content completo para reconstruir historial
- Persiste cada turno intermedio (assistant+tool_result) en DB
- La DB session se maneja manualmente por el SSE lifecycle
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
        self.model = settings.CLAUDE_MODEL

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
- Presenta las sugerencias numeradas para que el usuario elija.
- Cuando listes voces o música, presenta la información de forma amigable.
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

                # ─── Stream response from Claude ───
                assistant_content_blocks = []
                assistant_text_parts = []  # Accumulate text per-block
                tool_use_blocks = []
                current_text_index = -1
                current_tool_input_json = ""
                current_tool_name = ""
                current_tool_id = ""

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
                                # Stream text word by word
                                assistant_text_parts[current_text_index] += event.delta.text
                                yield self._sse_event("text_delta", {"text": event.delta.text})
                            elif event.delta.type == "input_json_delta":
                                current_tool_input_json += event.delta.partial_json

                        elif event.type == "content_block_stop":
                            # Finalize text block
                            if current_text_index >= 0 and current_text_index < len(assistant_content_blocks):
                                if assistant_content_blocks[current_text_index]["type"] == "text":
                                    assistant_content_blocks[current_text_index]["text"] = assistant_text_parts[current_text_index]

                            # Finalize tool_use block
                            if current_tool_name:
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

                # Collect full text from this iteration
                iteration_text = "".join(assistant_text_parts)

                # ─── If no tool_use, conversation turn is done ───
                if not tool_use_blocks:
                    # Save final assistant message
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
                    break

                # ─── Tools were used: persist this intermediate turn ───
                # Save assistant message with tool_use blocks
                intermediate_assistant = ChatMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=iteration_text,
                    raw_content=assistant_content_blocks,
                )
                db.add(intermediate_assistant)

                # Add to Claude message history
                messages.append({"role": "assistant", "content": assistant_content_blocks})

                # ─── Execute tools ───
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

            await db.commit()
            yield self._sse_event("message_end", {"conversation_id": conversation.id})

        except Exception as e:
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
```

---

## Paso 5: Endpoints de Chat

### Archivo: `backend/app/api/v1/endpoints/chat.py`

```python
"""
Chat API Endpoints - SSE streaming + conversation management.

El endpoint /send crea su propia DB session (NO usa Depends(get_db))
porque StreamingResponse necesita la sesión abierta durante todo el stream.
Los demás endpoints usan Depends(get_db) normalmente (auto-commit al final).
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, AsyncSessionLocal
from app.models.chat import ChatConversation, ChatMessage
from app.services.chat.chat_service import chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatSendRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None


class ConversationSummary(BaseModel):
    id: int
    title: Optional[str]
    is_active: bool
    message_count: int
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    audio_id: Optional[int] = None
    audio_url: Optional[str] = None
    created_at: str


@router.post("/send", summary="Send chat message (SSE stream)")
async def send_message(request: ChatSendRequest):
    """SSE stream: message_start, text_delta, tool_start, tool_result, audio_generated, message_end, error"""
    logger.info(f"Chat message: {request.message[:50]}...")

    async def event_generator():
        async with AsyncSessionLocal() as db:
            try:
                async for event in chat_service.send_message(
                    user_message=request.message,
                    conversation_id=request.conversation_id,
                    db=db,
                ):
                    yield event
            except Exception as e:
                logger.error(f"SSE generator error: {e}", exc_info=True)
                await db.rollback()
                import json
                yield f"event: error\ndata: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """List recent conversations (uses subquery for message count)."""
    msg_count = (
        select(func.count(ChatMessage.id))
        .where(ChatMessage.conversation_id == ChatConversation.id)
        .correlate(ChatConversation)
        .scalar_subquery()
    )
    result = await db.execute(
        select(ChatConversation, msg_count.label("message_count"))
        .filter(ChatConversation.is_active == True)
        .order_by(ChatConversation.updated_at.desc())
        .limit(limit)
    )
    return [
        ConversationSummary(
            id=conv.id, title=conv.title, is_active=conv.is_active,
            message_count=count,
            created_at=conv.created_at.isoformat() if conv.created_at else "",
            updated_at=conv.updated_at.isoformat() if conv.updated_at else "",
        )
        for conv, count in result.all()
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Get messages with audio_url resolved for playback."""
    result = await db.execute(
        select(ChatConversation).filter(ChatConversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    msg_result = await db.execute(
        select(ChatMessage)
        .filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.role.in_(["user", "assistant"]),
        )
        .order_by(ChatMessage.created_at)
    )
    messages = msg_result.scalars().all()

    return {
        "id": conversation.id,
        "title": conversation.title,
        "is_active": conversation.is_active,
        "messages": [
            MessageResponse(
                id=m.id, role=m.role, content=m.content,
                audio_id=m.audio_id,
                audio_url=f"/storage/audio/{m.audio.filename}" if m.audio_id and m.audio else None,
                created_at=m.created_at.isoformat() if m.created_at else "",
            )
            for m in messages
        ],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Soft-delete (get_db auto-commits)."""
    result = await db.execute(
        select(ChatConversation).filter(ChatConversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    conversation.is_active = False
    return {"success": True, "message": "Conversación eliminada"}
```

### Registrar router en `backend/app/api/v1/api.py`

```python
from app.api.v1.endpoints import chat
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
```

---

## Paso 6: Estructura de archivos

```
backend/app/services/chat/
├── __init__.py              # vacío
├── chat_service.py          # Paso 4
├── tools.py                 # Paso 2
└── tool_executor.py         # Paso 3

backend/app/services/audio/
├── generator.py             # NUEVO (Paso 0)
├── jingle.py                # existente
└── utils.py                 # existente
```

```bash
mkdir -p backend/app/services/chat
touch backend/app/services/chat/__init__.py
```

---

## Verificación

```bash
# Iniciar backend
cd /var/www/mediaflow-v2/backend && source venv/bin/activate
uvicorn app.main:app --reload --port 3001

# Test SSE stream (texto debe llegar palabra por palabra)
curl -N -X POST http://localhost:3001/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, qué voces tienes disponibles?"}'

# Test conversaciones
curl http://localhost:3001/api/v1/chat/conversations
curl http://localhost:3001/api/v1/chat/conversations/1

# Test continuación
curl -N -X POST http://localhost:3001/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Genera un spot de pizzas 2x1", "conversation_id": 1}'
```

### Checklist

- [ ] `generate_audio_message()` implementado y endpoint original refactorizado
- [ ] Migración de DB ejecutada
- [ ] `/api/v1/chat/send` retorna SSE con texto palabra por palabra
- [ ] Claude invoca herramientas correctamente
- [ ] Multi-turno funciona (Claude recuerda tools ejecutadas)
- [ ] Audio URL se resuelve al cargar conversación
- [ ] No hay warnings de DB session en logs
- [ ] El endpoint aparece en `/api/docs`

---

## Notas

1. **requirements.txt** dice `anthropic==0.7.0` pero la versión instalada es **0.74.1**. Actualizar: `pip freeze | grep anthropic > /tmp/v && cat /tmp/v` y actualizar requirements.txt.

2. **Nginx SSE**: Si hay reverse proxy, desactivar buffering:
   ```nginx
   location /api/v1/chat/ {
       proxy_pass http://127.0.0.1:3001;
       proxy_buffering off;
       proxy_cache off;
       proxy_set_header Connection '';
       proxy_http_version 1.1;
       chunked_transfer_encoding off;
   }
   ```

3. **Campos reales del modelo Schedule**: `specific_times` (no schedule_times), `days_of_week` (no schedule_days). Para tipo "once", `start_date` es la fecha/hora de ejecución.

4. **AzuraCast**: Import correcto es `from app.services.azuracast.client import azuracast_client`, método `send_audio_to_radio(file_path)`.

---

## Anexo: Revisión contra codebase real (2026-02-27)

Revisión del documento contra el código existente. Todos los imports, modelos y servicios referenciados fueron verificados.

### Lo que está correcto

- Arquitectura SSE con session manual (`AsyncSessionLocal`) — necesario porque `StreamingResponse` vive más que el ciclo de `Depends(get_db)`.
- Modelos `ChatConversation`/`ChatMessage` compatibles con `Base` y `TimestampMixin` existentes en `db/base.py`.
- Campos de `AudioMessage`, `VoiceSettings`, `Category`, `Schedule`, `MusicTrack` referenciados en el tool_executor coinciden con los modelos reales.
- `raw_content` JSON para reconstruir multi-turn con tool_use es la forma correcta.
- Todos los singletons referenciados existen: `claude_service`, `ai_client_manager`, `voice_manager`, `jingle_service`, `azuracast_client`.
- Patrón de registro de router en `api.py` es consistente con los demás.

### Problemas a corregir

#### P1: `requirements.txt` — Hacer ANTES de empezar
`requirements.txt` dice `anthropic==0.7.0`. Esa versión NO tiene `AsyncAnthropic` ni `messages.stream()`. La versión instalada real es ~0.74.1. **Actualizar requirements.txt como primer paso**, no como nota al pie.

#### P2: Paso 0 (`generator.py`) subestima la complejidad
El stub de 6 pasos omite lógica real de `audio.py` (líneas 119-343):
- Volume adjustment con pydub (líneas 208-215)
- TTS silence padding intro/outro desde `voice.tts_settings` (líneas 218-235)
- Guardado de `voice_settings_snapshot` en AudioMessage
- Cálculo de `file_size`, `sample_rate`, `bitrate`, `format`
- `cleanup_old_temporary_messages()` (mantiene max 50 temporales)

**Acción**: Al implementar, copiar toda la lógica de `audio.py` líneas 119-343, no solo el pseudo-código del stub.

#### P3: `save_to_library` — Semántica incorrecta
```python
audio.is_favorite = True  # ← Esto marca como favorito, NO guarda en biblioteca
```
Revisar qué hace el endpoint real `PATCH /{audio_id}/save-to-library` en `audio.py` y replicar esa lógica exacta.

#### P4: `content_block_stop` — Bug menor en streaming parser
Cuando `content_block_stop` llega para un tool_use block, el código también ejecuta la rama de finalizar text block (líneas 711-713) porque no hay `else`. Agregar separación:
```python
elif event.type == "content_block_stop":
    if current_tool_name:
        # Finalize tool_use block
        ...
    elif current_text_index >= 0:
        # Finalize text block
        ...
```

#### P5: Falta `db.rollback()` en `ChatService.send_message()`
El `except` solo hace `yield error event`. El rollback está en el `event_generator()` del endpoint, pero si `db.commit()` falla dentro de `send_message()`, no hay rollback explícito ahí. Agregar:
```python
except Exception as e:
    await db.rollback()
    logger.error(f"Chat error: {e}", exc_info=True)
    yield self._sse_event("error", {"message": str(e)})
```

#### P6: Verificar `services/audio/__init__.py`
El documento no menciona si `services/audio/` ya tiene `__init__.py`. Verificar antes de crear `generator.py`.

### Mejoras opcionales

1. **`generate_text_suggestions`** — Pasar `word_limit` basado en `duration` para sugerencias más precisas. El método real `generate_announcements()` lo soporta.
2. **Timeout en streaming loop** — 5 iteraciones de tools × (llamada API + ejecución) puede superar 30s. Considerar timeout global.
3. **`list_conversations` query** — Funciona correctamente, el unpacking `(conv, count)` de la subquery correlada es válido.

---

## Anexo 2: Análisis de riesgo para funcionalidad existente

### Veredicto: Riesgo BAJO — todo es aditivo excepto Paso 0

| Cambio | Toca código existente | Riesgo |
|--------|-----------------------|--------|
| Modelos `ChatConversation`/`ChatMessage` | No — tabla nueva | Ninguno |
| `services/chat/` (tools, executor, service) | No — directorio nuevo | Ninguno |
| Endpoint `/api/v1/chat/` | No — ruta nueva | Ninguno |
| Router en `api.py` | Sí — 1 línea `include_router` | Ninguno |
| **Paso 0: extraer `generator.py`** | **Sí — refactoriza `audio.py`** | **MEDIO** |

### Paso 0 es el único punto de riesgo

Si la extracción de lógica de `audio.py` (225 líneas reales) tiene un bug, **se rompe la generación de audio en toda la app**. Errores específicos del documento:

1. **`display_name=request.display_name`** en el endpoint refactorizado — `AudioGenerateRequest` no tiene ese campo. Dará `AttributeError`.
2. **El stub de `generator.py` es pseudo-código de 24 líneas** — la lógica real incluye: volume adjustment (pydub), silence padding intro/outro, `voice_settings_snapshot`, `cleanup_old_temporary_messages()`, cálculo de `file_size`/`sample_rate`/`bitrate`. Omitir esto degrada la calidad del audio.

**Recomendación**: Postergar Paso 0. El `tool_executor` puede reutilizar la lógica inline directamente o hacer HTTP call interno al endpoint existente. Refactorizar después, cuando el chat funcione.

### Bug crítico pre-existente: `requirements.txt`

`requirements.txt` dice `anthropic==0.7.0` pero la versión instalada es `0.74.1`. Si alguien reinstala dependencias, se rompe tanto el chat nuevo como el `claude_service` existente. **Actualizar antes de cualquier implementación.**
