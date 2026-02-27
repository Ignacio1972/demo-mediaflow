"""
Tests for Chat REST endpoints (excluding SSE streaming).

Tests conversation listing, retrieval, soft-delete, and message filtering.
Data is inserted directly into DB, bypassing ChatService.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatConversation, ChatMessage
from app.models.audio import AudioMessage

from tests.conftest import make_audio_message, make_conversation, make_chat_message

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helper to insert data via client's session factory
# ---------------------------------------------------------------------------

async def _seed(client, *objs):
    """Insert objects via the test client's session factory and return them refreshed."""
    factory = client._test_session_factory
    async with factory() as session:
        for obj in objs:
            session.add(obj)
        await session.commit()
        for obj in objs:
            await session.refresh(obj)
    return objs


# ---------------------------------------------------------------------------
# GET /api/v1/chat/conversations
# ---------------------------------------------------------------------------

async def test_list_conversations_empty(client):
    """Empty DB returns empty conversation list."""
    resp = await client.get("/api/v1/chat/conversations")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_conversations_with_data(client):
    """Returns conversations with correct message_count."""
    conv = ChatConversation(title="Test conv")
    await _seed(client, conv)

    # Add messages
    m1 = ChatMessage(conversation_id=conv.id, role="user", content="Hello")
    m2 = ChatMessage(conversation_id=conv.id, role="assistant", content="Hi there")
    m3 = ChatMessage(conversation_id=conv.id, role="tool_result", content="")
    await _seed(client, m1, m2, m3)

    resp = await client.get("/api/v1/chat/conversations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == conv.id
    assert data[0]["title"] == "Test conv"
    assert data[0]["message_count"] == 3  # all messages count


async def test_list_conversations_excludes_inactive(client):
    """Inactive conversations are not listed."""
    active = ChatConversation(title="Active")
    inactive = ChatConversation(title="Inactive", is_active=False)
    await _seed(client, active, inactive)

    resp = await client.get("/api/v1/chat/conversations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Active"


# ---------------------------------------------------------------------------
# GET /api/v1/chat/conversations/{id}
# ---------------------------------------------------------------------------

async def test_get_conversation_messages(client):
    """Returns messages filtering user and assistant roles only."""
    conv = ChatConversation(title="Detail test")
    await _seed(client, conv)

    msgs = [
        ChatMessage(conversation_id=conv.id, role="user", content="Hi"),
        ChatMessage(conversation_id=conv.id, role="assistant", content="Hello!"),
        ChatMessage(conversation_id=conv.id, role="tool_result", content="{}"),
        ChatMessage(conversation_id=conv.id, role="user", content="Generate audio"),
    ]
    await _seed(client, *msgs)

    resp = await client.get(f"/api/v1/chat/conversations/{conv.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == conv.id
    assert data["title"] == "Detail test"
    # Only user and assistant messages
    assert len(data["messages"]) == 3
    roles = [m["role"] for m in data["messages"]]
    assert "tool_result" not in roles


async def test_get_conversation_not_found(client):
    """404 for nonexistent conversation."""
    resp = await client.get("/api/v1/chat/conversations/99999")
    assert resp.status_code == 404


async def test_get_conversation_audio_url(client):
    """Messages with audio_id have audio_url resolved."""
    audio = make_audio_message(filename="chat_audio.mp3")
    conv = ChatConversation(title="Audio test")
    await _seed(client, audio, conv)

    msg = ChatMessage(
        conversation_id=conv.id, role="assistant",
        content="Here is your audio", audio_id=audio.id,
    )
    await _seed(client, msg)

    resp = await client.get(f"/api/v1/chat/conversations/{conv.id}")
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["audio_url"] == f"/storage/audio/chat_audio.mp3"
    assert messages[0]["audio_id"] == audio.id


async def test_get_conversation_no_audio_url_when_no_audio(client):
    """Messages without audio_id have audio_url=None."""
    conv = ChatConversation(title="No audio")
    await _seed(client, conv)

    msg = ChatMessage(conversation_id=conv.id, role="assistant", content="Just text")
    await _seed(client, msg)

    resp = await client.get(f"/api/v1/chat/conversations/{conv.id}")
    messages = resp.json()["messages"]
    assert messages[0]["audio_url"] is None
    assert messages[0]["audio_id"] is None


# ---------------------------------------------------------------------------
# DELETE /api/v1/chat/conversations/{id}
# ---------------------------------------------------------------------------

async def test_delete_conversation_soft_delete(client):
    """DELETE sets is_active=False but record stays in DB."""
    conv = ChatConversation(title="To delete")
    await _seed(client, conv)

    resp = await client.delete(f"/api/v1/chat/conversations/{conv.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

    # Verify it's soft-deleted (not in list)
    list_resp = await client.get("/api/v1/chat/conversations")
    assert len(list_resp.json()) == 0

    # But still in DB (via direct query)
    factory = client._test_session_factory
    async with factory() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(ChatConversation).filter(ChatConversation.id == conv.id)
        )
        db_conv = result.scalar_one()
        assert db_conv.is_active is False


async def test_delete_conversation_not_found(client):
    """DELETE on nonexistent conversation returns 404."""
    resp = await client.delete("/api/v1/chat/conversations/99999")
    assert resp.status_code == 404
