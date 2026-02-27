"""
Tests for ChatService internal methods.

Tests conversation management, history building, and SSE formatting.
Claude API is NOT called - we test helper methods directly.
"""
import json
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from sqlalchemy import select

from app.models.chat import ChatConversation, ChatMessage
from app.services.chat.chat_service import ChatService, MAX_HISTORY_MESSAGES

from tests.conftest import make_conversation, make_chat_message

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def service():
    """ChatService with mocked Anthropic client (not used in these tests)."""
    with patch("app.services.chat.chat_service.AsyncAnthropic"):
        svc = ChatService()
    return svc


# ---------------------------------------------------------------------------
# _get_or_create_conversation
# ---------------------------------------------------------------------------

async def test_get_or_create_new_conversation(db_session, service):
    """Creates new conversation when conversation_id is None."""
    conv = await service._get_or_create_conversation(
        conversation_id=None,
        first_message="Hello world",
        db=db_session,
    )

    assert conv.id is not None
    assert conv.title == "Hello world"


async def test_get_or_create_new_conversation_title_truncated(db_session, service):
    """Long messages get truncated to 80 chars + '...' in title."""
    long_msg = "A" * 100
    conv = await service._get_or_create_conversation(
        conversation_id=None,
        first_message=long_msg,
        db=db_session,
    )

    assert len(conv.title) == 83  # 80 + "..."
    assert conv.title.endswith("...")


async def test_get_or_create_existing_conversation(db_session, service):
    """Returns existing conversation when valid conversation_id is given."""
    existing = ChatConversation(title="Existing")
    db_session.add(existing)
    await db_session.flush()

    conv = await service._get_or_create_conversation(
        conversation_id=existing.id,
        first_message="Follow up",
        db=db_session,
    )

    assert conv.id == existing.id
    assert conv.title == "Existing"


async def test_get_or_create_nonexistent_id_creates_new(db_session, service):
    """Creates new conversation when conversation_id doesn't exist in DB."""
    conv = await service._get_or_create_conversation(
        conversation_id=99999,
        first_message="Fresh start",
        db=db_session,
    )

    assert conv.id is not None
    assert conv.id != 99999
    assert conv.title == "Fresh start"


# ---------------------------------------------------------------------------
# _build_messages_history
# ---------------------------------------------------------------------------

async def test_build_messages_history_basic(db_session, service):
    """Reconstructs user/assistant messages correctly."""
    conv = ChatConversation(title="History test")
    db_session.add(conv)
    await db_session.flush()

    db_session.add(ChatMessage(
        conversation_id=conv.id, role="user", content="Hi",
    ))
    db_session.add(ChatMessage(
        conversation_id=conv.id, role="assistant", content="Hello!",
    ))
    await db_session.flush()

    messages = await service._build_messages_history(conv.id, db_session)

    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "Hi"}
    assert messages[1] == {"role": "assistant", "content": "Hello!"}


async def test_build_messages_history_truncates(db_session, service):
    """History is truncated to MAX_HISTORY_MESSAGES."""
    conv = ChatConversation(title="Long history")
    db_session.add(conv)
    await db_session.flush()

    # Create more messages than the limit
    for i in range(MAX_HISTORY_MESSAGES + 10):
        role = "user" if i % 2 == 0 else "assistant"
        db_session.add(ChatMessage(
            conversation_id=conv.id, role=role,
            content=f"Message {i}",
        ))
    await db_session.flush()

    messages = await service._build_messages_history(conv.id, db_session)

    assert len(messages) == MAX_HISTORY_MESSAGES


async def test_build_messages_history_preserves_raw_content(db_session, service):
    """Raw content (tool_use structure) is preserved for assistant messages."""
    conv = ChatConversation(title="Tool history")
    db_session.add(conv)
    await db_session.flush()

    raw = [
        {"type": "text", "text": "Let me help"},
        {"type": "tool_use", "id": "tu_1", "name": "list_voices", "input": {}},
    ]
    db_session.add(ChatMessage(
        conversation_id=conv.id, role="assistant",
        content="Let me help", raw_content=raw,
    ))
    await db_session.flush()

    messages = await service._build_messages_history(conv.id, db_session)

    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    # Should use raw_content (list) instead of plain content (string)
    assert isinstance(messages[0]["content"], list)
    assert messages[0]["content"][0]["type"] == "text"
    assert messages[0]["content"][1]["type"] == "tool_use"


async def test_build_messages_history_tool_result(db_session, service):
    """tool_result messages are reconstructed as user messages with raw_content."""
    conv = ChatConversation(title="Tool result")
    db_session.add(conv)
    await db_session.flush()

    tool_result_raw = [
        {"type": "tool_result", "tool_use_id": "tu_1", "content": '{"success": true}'},
    ]
    db_session.add(ChatMessage(
        conversation_id=conv.id, role="user", content="First message",
    ))
    db_session.add(ChatMessage(
        conversation_id=conv.id, role="assistant", content="Using tool",
        raw_content=[{"type": "text", "text": "Using tool"}, {"type": "tool_use", "id": "tu_1", "name": "test", "input": {}}],
    ))
    db_session.add(ChatMessage(
        conversation_id=conv.id, role="tool_result", content="",
        raw_content=tool_result_raw,
    ))
    await db_session.flush()

    messages = await service._build_messages_history(conv.id, db_session)

    assert len(messages) == 3
    # tool_result becomes a user message with raw content
    assert messages[2]["role"] == "user"
    assert messages[2]["content"][0]["type"] == "tool_result"


async def test_build_messages_history_assistant_plain_content(db_session, service):
    """Assistant without raw_content uses plain content string."""
    conv = ChatConversation(title="Plain")
    db_session.add(conv)
    await db_session.flush()

    db_session.add(ChatMessage(
        conversation_id=conv.id, role="assistant",
        content="Simple response", raw_content=None,
    ))
    await db_session.flush()

    messages = await service._build_messages_history(conv.id, db_session)

    assert len(messages) == 1
    assert messages[0]["content"] == "Simple response"
    assert isinstance(messages[0]["content"], str)


# ---------------------------------------------------------------------------
# _sse_event
# ---------------------------------------------------------------------------

async def test_sse_event_format(service):
    """SSE events have correct format: event: type\\ndata: json\\n\\n"""
    event = service._sse_event("text_delta", {"text": "Hello"})

    assert event.startswith("event: text_delta\n")
    assert "data: " in event
    assert event.endswith("\n\n")

    # Parse data line
    lines = event.strip().split("\n")
    assert lines[0] == "event: text_delta"
    data_json = lines[1].removeprefix("data: ")
    parsed = json.loads(data_json)
    assert parsed["type"] == "text_delta"
    assert parsed["text"] == "Hello"


async def test_sse_event_message_start(service):
    """message_start event includes conversation_id."""
    event = service._sse_event("message_start", {"conversation_id": 42})
    data = json.loads(event.strip().split("\n")[1].removeprefix("data: "))
    assert data["type"] == "message_start"
    assert data["conversation_id"] == 42


async def test_sse_event_handles_non_serializable(service):
    """SSE event handles datetime and other non-serializable types via default=str."""
    dt = datetime(2025, 1, 1, 12, 0, 0)
    event = service._sse_event("test", {"timestamp": dt})
    data = json.loads(event.strip().split("\n")[1].removeprefix("data: "))
    assert "2025" in data["timestamp"]
