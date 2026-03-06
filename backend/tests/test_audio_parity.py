"""
Tests for audio generation parity between:
  1. POST /api/v1/audio/generate (REST endpoint in audio.py)
  2. ToolExecutor.execute("generate_audio", ...) (chat tool in tool_executor.py)

Both code paths should produce AudioMessage records with equivalent structure.
This is the critical test for the upcoming Step 0 refactor.

All tests use the client fixture (single engine) so both paths share the same DB.
"""
import json
import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import select

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.services.chat.tool_executor import ToolExecutor

from tests.conftest import make_voice

pytestmark = pytest.mark.asyncio

# Both code paths now delegate to the shared generator module
GEN = "app.services.audio.generator"

# Shared fake data for both paths
FAKE_AUDIO_BYTES = b"\xff\xfb\x90\x00" + b"\x00" * 500
FAKE_DURATION_MS = 7500  # 7.5 seconds
FAKE_FILE_SIZE = 504
FAKE_TEXT = "Atencion clientes: oferta especial en el sector de electronica hoy"
VOICE_ID = "parity_voice"
VOICE_NAME = "Parity Voice"


def _make_voice_obj():
    return make_voice(
        id=VOICE_ID, name=VOICE_NAME,
        elevenlabs_id="el_parity_123",
        style=10.0, stability=60.0, similarity_boost=80.0,
        speed=1.1, volume_adjustment=0.0,
    )


def _fake_effective_settings():
    return {
        "style": 10.0, "stability": 60.0, "similarity_boost": 80.0,
        "speed": 1.1, "volume_adjustment": 0.0,
    }


def _fake_snapshot():
    return json.dumps({
        "voice_id": VOICE_ID, "voice_name": VOICE_NAME,
        "elevenlabs_id": "el_parity_123",
        "style": 10.0, "stability": 60.0, "similarity_boost": 80.0,
        "use_speaker_boost": True, "speed": 1.1,
        "volume_adjustment": 0.0, "jingle_settings": None,
    })


async def _seed_voice(client):
    """Insert the parity test voice into the client's database."""
    factory = client._test_session_factory
    async with factory() as session:
        session.add(_make_voice_obj())
        await session.commit()


async def _generate_via_tool(client) -> AudioMessage:
    """Generate audio via ToolExecutor using client's DB and return the AudioMessage."""
    executor = ToolExecutor()
    voice_obj = _make_voice_obj()
    fake_settings = _fake_effective_settings()

    mock_segment = MagicMock()
    mock_segment.__len__ = lambda self: FAKE_DURATION_MS

    # Use a fixed timestamp so filenames are predictable and unique vs endpoint
    tool_dt = datetime(2026, 1, 1, 10, 0, 0)

    factory = client._test_session_factory
    async with factory() as session:
        with patch(
            f"{GEN}.voice_manager.generate_with_voice",
            new_callable=AsyncMock,
            return_value=(FAKE_AUDIO_BYTES, voice_obj, fake_settings),
        ), patch(
            f"{GEN}.voice_manager.get_voice_settings_snapshot",
            return_value=_fake_snapshot(),
        ), patch(
            f"{GEN}.AudioSegment"
        ) as mock_pydub, patch(
            f"{GEN}.os.makedirs",
        ), patch(
            f"{GEN}.os.path.getsize",
            return_value=FAKE_FILE_SIZE,
        ), patch(
            f"{GEN}.datetime"
        ) as mock_dt, patch("builtins.open", MagicMock()):
            mock_dt.now.return_value = tool_dt
            mock_dt.fromisoformat = datetime.fromisoformat
            mock_pydub.from_file.return_value = mock_segment

            result = await executor.execute(
                "generate_audio",
                {"text": FAKE_TEXT, "voice_id": VOICE_ID},
                session,
            )
            await session.commit()

        assert result["success"] is True
        audio_id = result["data"]["audio_id"]

    # Read back in a fresh session
    async with factory() as session:
        db_result = await session.execute(
            select(AudioMessage).filter(AudioMessage.id == audio_id)
        )
        return db_result.scalar_one()


async def _generate_via_endpoint(client) -> AudioMessage:
    """Generate audio via REST endpoint and return the AudioMessage."""
    voice_obj = _make_voice_obj()
    fake_settings = _fake_effective_settings()

    mock_segment = MagicMock()
    mock_segment.__len__ = lambda self: FAKE_DURATION_MS

    # Use a different fixed timestamp than the tool path to avoid UNIQUE conflict
    endpoint_dt = datetime(2026, 1, 1, 11, 0, 0)

    with patch(
        f"{GEN}.voice_manager.generate_with_voice",
        new_callable=AsyncMock,
        return_value=(FAKE_AUDIO_BYTES, voice_obj, fake_settings),
    ), patch(
        f"{GEN}.voice_manager.get_voice_settings_snapshot",
        return_value=_fake_snapshot(),
    ), patch(
        f"{GEN}.AudioSegment"
    ) as mock_pydub, patch(
        f"{GEN}.os.makedirs",
    ), patch(
        f"{GEN}.os.path.getsize",
        return_value=FAKE_FILE_SIZE,
    ), patch(
        f"{GEN}.datetime"
    ) as mock_dt, patch("builtins.open", MagicMock()):
        mock_dt.now.return_value = endpoint_dt
        mock_pydub.from_file.return_value = mock_segment

        resp = await client.post("/api/v1/audio/generate", json={
            "text": FAKE_TEXT,
            "voice_id": VOICE_ID,
        })

    assert resp.status_code == 201
    data = resp.json()
    audio_id = data["audio_id"]

    factory = client._test_session_factory
    async with factory() as session:
        db_result = await session.execute(
            select(AudioMessage).filter(AudioMessage.id == audio_id)
        )
        return db_result.scalar_one()


# ---------------------------------------------------------------------------
# Parity tests
# ---------------------------------------------------------------------------

async def test_parity_both_paths_create_audio(client):
    """Both paths successfully create AudioMessage records."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio is not None
    assert endpoint_audio is not None


async def test_parity_same_status(client):
    """Both paths produce status='ready'."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio.status == "ready"
    assert endpoint_audio.status == "ready"


async def test_parity_same_voice_id(client):
    """Both paths store the same voice_id."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio.voice_id == VOICE_ID
    assert endpoint_audio.voice_id == VOICE_ID


async def test_parity_same_text_and_display_name(client):
    """Both paths store the same original_text and compute same display_name."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio.original_text == FAKE_TEXT
    assert endpoint_audio.original_text == FAKE_TEXT

    # Display name: first 50 chars + "..." if text > 50 chars
    expected_display = FAKE_TEXT[:50] + "..."
    assert tool_audio.display_name == expected_display
    assert endpoint_audio.display_name == expected_display


async def test_parity_same_format_and_jingle_defaults(client):
    """Both paths default to format=mp3 and has_jingle=False."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio.format == "mp3"
    assert endpoint_audio.format == "mp3"
    assert tool_audio.has_jingle is False
    assert endpoint_audio.has_jingle is False


async def test_parity_filename_structure(client):
    """Both paths produce filenames with tts_ prefix and voice_id suffix."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    # Both should follow pattern: tts_YYYYMMDD_HHMMSS_{voice_id}.mp3
    assert tool_audio.filename.startswith("tts_")
    assert tool_audio.filename.endswith(f"_{VOICE_ID}.mp3")
    assert endpoint_audio.filename.startswith("tts_")
    assert endpoint_audio.filename.endswith(f"_{VOICE_ID}.mp3")


async def test_parity_voice_settings_snapshot(client):
    """Both paths store a voice_settings_snapshot."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio.voice_settings_snapshot is not None
    assert endpoint_audio.voice_settings_snapshot is not None

    # Parse and compare key fields
    tool_snap = json.loads(tool_audio.voice_settings_snapshot)
    endpoint_snap = json.loads(endpoint_audio.voice_settings_snapshot)

    assert tool_snap["voice_id"] == endpoint_snap["voice_id"]
    assert tool_snap["style"] == endpoint_snap["style"]
    assert tool_snap["stability"] == endpoint_snap["stability"]


async def test_parity_volume_adjustment(client):
    """Both paths store the same volume_adjustment."""
    await _seed_voice(client)

    tool_audio = await _generate_via_tool(client)
    endpoint_audio = await _generate_via_endpoint(client)

    assert tool_audio.volume_adjustment == endpoint_audio.volume_adjustment
    assert tool_audio.volume_adjustment == 0.0
