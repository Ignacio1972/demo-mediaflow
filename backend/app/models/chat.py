"""
Chat conversation and message models.

raw_content stores the full Anthropic structure (text + tool_use + tool_result)
to reconstruct multi-turn history correctly.
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
    content = Column(Text, nullable=False, default="")  # Visible text

    # Raw Anthropic structure for reconstructing history with tool_use
    # assistant: [{type:"text",text:"..."}, {type:"tool_use",id:"...",name:"...",input:{}}]
    # tool_result: [{type:"tool_result",tool_use_id:"...",content:"..."}]
    raw_content = Column(JSON, nullable=True)

    audio_id = Column(Integer, ForeignKey("audio_messages.id"), nullable=True)
    audio = relationship("AudioMessage", lazy="joined")

    conversation = relationship("ChatConversation", back_populates="messages")
