"""
Tests for ToolExecutor - each tool tested in isolation with mocked external services.
"""
import json
import os
import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import select

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.models.music_track import MusicTrack
from app.models.category import Category
from app.models.schedule import Schedule
from app.services.chat.tool_executor import ToolExecutor

from tests.conftest import (
    make_voice, make_category, make_audio_message, make_music_track,
)

pytestmark = pytest.mark.asyncio

# Shared generator module path for patches
GEN = "app.services.audio.generator"


@pytest_asyncio.fixture
async def executor():
    return ToolExecutor()


# ---------------------------------------------------------------------------
# generate_text_suggestions
# ---------------------------------------------------------------------------

async def test_tool_generate_text_suggestions(db_session, executor):
    """generate_text_suggestions calls claude_service and returns suggestions."""
    fake_suggestions = [
        {"id": 1, "text": "Oferta especial", "char_count": 15, "word_count": 2},
        {"id": 2, "text": "Descuento hoy", "char_count": 13, "word_count": 2},
    ]
    with patch(
        "app.services.chat.tool_executor.claude_service.generate_announcements",
        new_callable=AsyncMock,
        return_value=fake_suggestions,
    ), patch(
        "app.services.chat.tool_executor.ai_client_manager.get_active_client",
        new_callable=AsyncMock,
        return_value=None,
    ):
        result = await executor.execute(
            "generate_text_suggestions",
            {"context": "oferta de zapatos"},
            db_session,
        )

    assert result["success"] is True
    assert len(result["data"]) == 2
    assert result["data"][0]["text"] == "Oferta especial"


# ---------------------------------------------------------------------------
# generate_audio
# ---------------------------------------------------------------------------

async def test_tool_generate_audio(db_session, executor):
    """generate_audio creates AudioMessage in DB with correct fields."""
    voice = make_voice(id="juan", name="Juan")
    db_session.add(voice)
    await db_session.flush()

    fake_audio_bytes = b"\xff\xfb\x90\x00" + b"\x00" * 500  # fake mp3 header
    fake_settings = {
        "style": 0.0, "stability": 50.0, "similarity_boost": 75.0,
        "speed": 1.0, "volume_adjustment": 0.0,
    }

    with patch(
        f"{GEN}.voice_manager.generate_with_voice",
        new_callable=AsyncMock,
        return_value=(fake_audio_bytes, voice, fake_settings),
    ), patch(
        f"{GEN}.voice_manager.get_voice_settings_snapshot",
        return_value='{"voice_id": "juan", "voice_name": "Juan"}',
    ), patch(
        f"{GEN}.AudioSegment"
    ) as mock_pydub, patch(
        f"{GEN}.os.makedirs",
    ), patch(
        f"{GEN}.os.path.getsize",
        return_value=504,
    ), patch("builtins.open", MagicMock()):
        # Mock AudioSegment.from_file to return a mock with len=5000 (5 seconds)
        mock_segment = MagicMock()
        mock_segment.__len__ = lambda self: 5000
        mock_pydub.from_file.return_value = mock_segment

        result = await executor.execute(
            "generate_audio",
            {"text": "Hola mundo", "voice_id": "juan"},
            db_session,
        )

    assert result["success"] is True
    assert result["data"]["voice_id"] == "juan"
    assert result["data"]["audio_id"] is not None
    assert "audio_url" in result["data"]

    # Verify DB record
    db_result = await db_session.execute(
        select(AudioMessage).filter(AudioMessage.id == result["data"]["audio_id"])
    )
    audio_msg = db_result.scalar_one()
    assert audio_msg.voice_id == "juan"
    assert audio_msg.original_text == "Hola mundo"
    assert audio_msg.status == "ready"
    assert audio_msg.display_name == "Hola mundo"


async def test_tool_generate_audio_default_voice(db_session, executor):
    """generate_audio without voice_id uses default voice."""
    default_voice = make_voice(id="default_v", name="Default", is_default=True)
    db_session.add(default_voice)
    await db_session.flush()

    fake_settings = {
        "style": 0.0, "stability": 50.0, "similarity_boost": 75.0,
        "speed": 1.0, "volume_adjustment": 0.0,
    }

    with patch(
        f"{GEN}.voice_manager.generate_with_voice",
        new_callable=AsyncMock,
        return_value=(b"\x00" * 100, default_voice, fake_settings),
    ), patch(
        f"{GEN}.voice_manager.get_voice_settings_snapshot",
        return_value='{"voice_name": "Default"}',
    ), patch(
        f"{GEN}.AudioSegment"
    ) as mock_pydub, patch(
        f"{GEN}.os.makedirs",
    ), patch(
        f"{GEN}.os.path.getsize",
        return_value=100,
    ), patch("builtins.open", MagicMock()):
        mock_segment = MagicMock()
        mock_segment.__len__ = lambda self: 3000
        mock_pydub.from_file.return_value = mock_segment

        result = await executor.execute(
            "generate_audio",
            {"text": "Sin voz especificada"},
            db_session,
        )

    assert result["success"] is True
    assert result["data"]["voice_id"] == "default_v"


async def test_tool_generate_audio_nonexistent_voice(db_session, executor):
    """generate_audio with nonexistent voice returns failure."""
    result = await executor.execute(
        "generate_audio",
        {"text": "Test", "voice_id": "nonexistent"},
        db_session,
    )
    assert result["success"] is False
    assert "no encontrada" in result["message"]


async def test_tool_generate_audio_inactive_voice(db_session, executor):
    """generate_audio with inactive voice returns failure."""
    voice = make_voice(id="inactive_v", name="Inactive", active=False)
    db_session.add(voice)
    await db_session.flush()

    result = await executor.execute(
        "generate_audio",
        {"text": "Test", "voice_id": "inactive_v"},
        db_session,
    )
    assert result["success"] is False
    assert "inactiva" in result["message"]


async def test_tool_generate_audio_no_voices_configured(db_session, executor):
    """generate_audio without voice_id and no voices in DB returns failure."""
    result = await executor.execute(
        "generate_audio",
        {"text": "Test sin voces"},
        db_session,
    )
    assert result["success"] is False
    assert "No hay voces" in result["message"]


# ---------------------------------------------------------------------------
# list_voices
# ---------------------------------------------------------------------------

async def test_tool_list_voices(db_session, executor):
    """list_voices returns only active voices."""
    db_session.add(make_voice(id="v1", name="Alpha", active=True))
    db_session.add(make_voice(id="v2", name="Beta", active=True))
    db_session.add(make_voice(id="v3", name="Gamma", active=False))
    await db_session.flush()

    result = await executor.execute("list_voices", {}, db_session)

    assert result["success"] is True
    assert len(result["data"]) == 2
    voice_ids = {v["id"] for v in result["data"]}
    assert "v1" in voice_ids
    assert "v2" in voice_ids
    assert "v3" not in voice_ids


# ---------------------------------------------------------------------------
# list_music_tracks
# ---------------------------------------------------------------------------

async def test_tool_list_music_tracks(db_session, executor):
    """list_music_tracks returns active tracks."""
    db_session.add(make_music_track(filename="a.mp3", display_name="Track A", active=True))
    db_session.add(make_music_track(filename="b.mp3", display_name="Track B", active=True))
    db_session.add(make_music_track(filename="c.mp3", display_name="Track C", active=False))
    await db_session.flush()

    result = await executor.execute("list_music_tracks", {}, db_session)

    assert result["success"] is True
    assert len(result["data"]) == 2
    names = {t["display_name"] for t in result["data"]}
    assert "Track A" in names
    assert "Track B" in names


# ---------------------------------------------------------------------------
# save_to_library
# ---------------------------------------------------------------------------

async def test_tool_save_to_library(db_session, executor):
    """save_to_library sets is_favorite=True on existing audio."""
    audio = make_audio_message(filename="save_test.mp3")
    db_session.add(audio)
    await db_session.flush()

    result = await executor.execute(
        "save_to_library",
        {"audio_id": audio.id},
        db_session,
    )

    assert result["success"] is True
    await db_session.refresh(audio)
    assert audio.is_favorite is True


async def test_tool_save_to_library_with_name_and_category(db_session, executor):
    """save_to_library updates display_name and category_id."""
    cat = make_category(id="promo", name="Promos")
    audio = make_audio_message(filename="save_name.mp3")
    db_session.add_all([cat, audio])
    await db_session.flush()

    result = await executor.execute(
        "save_to_library",
        {"audio_id": audio.id, "display_name": "Promo navidad", "category_id": "promo"},
        db_session,
    )

    assert result["success"] is True
    await db_session.refresh(audio)
    assert audio.display_name == "Promo navidad"
    assert audio.category_id == "promo"


async def test_tool_save_to_library_nonexistent(db_session, executor):
    """save_to_library with nonexistent audio_id returns failure."""
    result = await executor.execute(
        "save_to_library",
        {"audio_id": 99999},
        db_session,
    )
    assert result["success"] is False
    assert "no encontrado" in result["message"]


# ---------------------------------------------------------------------------
# create_schedule
# ---------------------------------------------------------------------------

async def test_tool_create_schedule_interval(db_session, executor):
    """create_schedule with type interval creates Schedule with interval_minutes."""
    audio = make_audio_message(filename="sched_int.mp3")
    db_session.add(audio)
    await db_session.flush()

    result = await executor.execute(
        "create_schedule",
        {
            "audio_id": audio.id,
            "schedule_type": "interval",
            "interval_minutes": 30,
        },
        db_session,
    )

    assert result["success"] is True
    schedule_id = result["data"]["schedule_id"]

    db_result = await db_session.execute(
        select(Schedule).filter(Schedule.id == schedule_id)
    )
    schedule = db_result.scalar_one()
    assert schedule.schedule_type == "interval"
    assert schedule.interval_minutes == 30
    assert schedule.active is True


async def test_tool_create_schedule_specific(db_session, executor):
    """create_schedule with type specific stores specific_times and days_of_week."""
    audio = make_audio_message(filename="sched_spec.mp3")
    db_session.add(audio)
    await db_session.flush()

    result = await executor.execute(
        "create_schedule",
        {
            "audio_id": audio.id,
            "schedule_type": "specific",
            "specific_times": ["09:00", "14:00"],
            "days_of_week": [0, 1, 2, 3, 4],
        },
        db_session,
    )

    assert result["success"] is True
    schedule_id = result["data"]["schedule_id"]

    db_result = await db_session.execute(
        select(Schedule).filter(Schedule.id == schedule_id)
    )
    schedule = db_result.scalar_one()
    assert schedule.schedule_type == "specific"
    assert schedule.specific_times == ["09:00", "14:00"]
    assert schedule.days_of_week == [0, 1, 2, 3, 4]


async def test_tool_create_schedule_nonexistent_audio(db_session, executor):
    """create_schedule with nonexistent audio returns failure."""
    result = await executor.execute(
        "create_schedule",
        {"audio_id": 99999, "schedule_type": "interval"},
        db_session,
    )
    assert result["success"] is False


# ---------------------------------------------------------------------------
# list_categories
# ---------------------------------------------------------------------------

async def test_tool_list_categories(db_session, executor):
    """list_categories returns only active categories."""
    db_session.add(make_category(id="c1", name="Cat1", active=True, order=1))
    db_session.add(make_category(id="c2", name="Cat2", active=True, order=2))
    db_session.add(make_category(id="c3", name="Cat3", active=False, order=3))
    await db_session.flush()

    result = await executor.execute("list_categories", {}, db_session)

    assert result["success"] is True
    assert len(result["data"]) == 2
    ids = {c["id"] for c in result["data"]}
    assert "c1" in ids
    assert "c2" in ids


# ---------------------------------------------------------------------------
# search_library
# ---------------------------------------------------------------------------

async def test_tool_search_library(db_session, executor):
    """search_library filters by query on favorite audios."""
    db_session.add(make_audio_message(
        filename="fav1.mp3", display_name="Oferta zapatos",
        original_text="Oferta de zapatos hoy", is_favorite=True,
    ))
    db_session.add(make_audio_message(
        filename="fav2.mp3", display_name="Promo ropa",
        original_text="Descuento en ropa", is_favorite=True,
    ))
    db_session.add(make_audio_message(
        filename="nofav.mp3", display_name="Oferta temporal",
        original_text="Oferta temporal", is_favorite=False,
    ))
    await db_session.flush()

    result = await executor.execute(
        "search_library",
        {"query": "zapatos"},
        db_session,
    )

    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["display_name"] == "Oferta zapatos"


async def test_tool_search_library_by_category(db_session, executor):
    """search_library filters by category_id."""
    cat = make_category(id="shoes", name="Shoes")
    db_session.add(cat)
    db_session.add(make_audio_message(
        filename="cat1.mp3", display_name="Audio 1",
        is_favorite=True, category_id="shoes",
    ))
    db_session.add(make_audio_message(
        filename="cat2.mp3", display_name="Audio 2",
        is_favorite=True, category_id=None,
    ))
    await db_session.flush()

    result = await executor.execute(
        "search_library",
        {"category_id": "shoes"},
        db_session,
    )

    assert result["success"] is True
    assert len(result["data"]) == 1


async def test_tool_search_library_empty(db_session, executor):
    """search_library returns empty list when no matches."""
    result = await executor.execute(
        "search_library",
        {"query": "nonexistent"},
        db_session,
    )
    assert result["success"] is True
    assert len(result["data"]) == 0


# ---------------------------------------------------------------------------
# send_to_radio
# ---------------------------------------------------------------------------

async def test_tool_send_to_radio(db_session, executor):
    """send_to_radio marks audio as sent_to_player when radio succeeds."""
    audio = make_audio_message(filename="radio_test.mp3")
    db_session.add(audio)
    await db_session.flush()

    with patch(
        "app.services.chat.tool_executor.azuracast_client",
        create=True,
    ) as mock_module:
        # The import is inside the method so we patch where it's imported
        with patch(
            "app.services.azuracast.client.azuracast_client.send_audio_to_radio",
            new_callable=AsyncMock,
            return_value={"success": True},
        ):
            result = await executor.execute(
                "send_to_radio",
                {"audio_id": audio.id},
                db_session,
            )

    assert result["success"] is True
    await db_session.refresh(audio)
    assert audio.sent_to_player is True


async def test_tool_send_to_radio_nonexistent(db_session, executor):
    """send_to_radio with nonexistent audio returns failure."""
    result = await executor.execute(
        "send_to_radio",
        {"audio_id": 99999},
        db_session,
    )
    assert result["success"] is False


# ---------------------------------------------------------------------------
# Unknown tool
# ---------------------------------------------------------------------------

async def test_tool_unknown(db_session, executor):
    """Executing an unknown tool returns failure."""
    result = await executor.execute("nonexistent_tool", {}, db_session)
    assert result["success"] is False
    assert "desconocida" in result["message"]


# ---------------------------------------------------------------------------
# list_schedules
# ---------------------------------------------------------------------------

async def test_tool_list_schedules(db_session, executor):
    """list_schedules returns active schedules."""
    audio = make_audio_message(filename="sched_list.mp3")
    db_session.add(audio)
    await db_session.flush()

    s1 = Schedule(
        audio_message_id=audio.id, schedule_type="interval",
        interval_minutes=60, active=True, start_date=datetime.now(),
    )
    s2 = Schedule(
        audio_message_id=audio.id, schedule_type="once",
        active=False, start_date=datetime.now(),
    )
    db_session.add_all([s1, s2])
    await db_session.flush()

    result = await executor.execute("list_schedules", {"active_only": True}, db_session)

    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["schedule_type"] == "interval"
