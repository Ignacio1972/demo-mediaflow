"""
Chat API Endpoints - SSE streaming + conversation management.

The /send endpoint creates its own DB session (NOT via Depends(get_db))
because StreamingResponse needs the session open during the entire stream.
Other endpoints use Depends(get_db) normally (auto-commit at end).
"""
import json
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
