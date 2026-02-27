"""
Shared test fixtures for MediaFlow tests.

Provides:
- Async SQLite in-memory database
- FastAPI test client with dependency override
- Common data factories (voices, categories, music tracks, audio messages)
"""
import os
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

# Set required env vars BEFORE importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("STORAGE_PATH", "/tmp/mediaflow-test/storage")
os.environ.setdefault("AUDIO_PATH", "/tmp/mediaflow-test/storage/audio")
os.environ.setdefault("MUSIC_PATH", "/tmp/mediaflow-test/storage/music")
os.environ.setdefault("TEMP_PATH", "/tmp/mediaflow-test/storage/temp")

from app.db.base import Base
from app.models import (  # noqa: E402 - import all models to register them
    VoiceSettings, Category, AudioMessage, Schedule, MusicTrack,
    ChatConversation, ChatMessage,
)
from app.db.session import get_db
from app.main import app


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_engine():
    """Create an async in-memory SQLite engine and create all tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provide an async database session for tests."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession,
        expire_on_commit=False, autocommit=False, autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(db_engine):
    """
    httpx.AsyncClient wired to the FastAPI app with DB dependency override.
    Each request gets its own session from the test engine.
    """
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession,
        expire_on_commit=False, autocommit=False, autoflush=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Attach session factory so tests can also insert data directly
        c._test_session_factory = session_factory  # type: ignore[attr-defined]
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Data factory helpers
# ---------------------------------------------------------------------------

def make_voice(
    id: str = "test_voice",
    name: str = "Test Voice",
    elevenlabs_id: str = "el_test_123",
    active: bool = True,
    is_default: bool = False,
    **kwargs,
) -> VoiceSettings:
    defaults = dict(
        id=id, name=name, elevenlabs_id=elevenlabs_id,
        active=active, is_default=is_default, order=0,
        style=0.0, stability=50.0, similarity_boost=75.0,
        use_speaker_boost=True, speed=1.0, volume_adjustment=0.0,
    )
    defaults.update(kwargs)
    return VoiceSettings(**defaults)


def make_category(
    id: str = "test_cat",
    name: str = "Test Category",
    active: bool = True,
    **kwargs,
) -> Category:
    defaults = dict(
        id=id, name=name, icon="📦", color="#FF0000",
        order=0, active=active,
    )
    defaults.update(kwargs)
    return Category(**defaults)


def make_audio_message(
    filename: str = "test_audio.mp3",
    display_name: str = "Test Audio",
    original_text: str = "Hello world",
    voice_id: str = "test_voice",
    **kwargs,
) -> AudioMessage:
    defaults = dict(
        filename=filename, display_name=display_name,
        file_path=f"/tmp/mediaflow-test/storage/audio/{filename}",
        file_size=1024, duration=5.0, format="mp3",
        original_text=original_text, voice_id=voice_id,
        status="ready", is_favorite=False, has_jingle=False,
        volume_adjustment=0.0,
    )
    defaults.update(kwargs)
    return AudioMessage(**defaults)


def make_music_track(
    filename: str = "test_music.mp3",
    display_name: str = "Test Music",
    active: bool = True,
    is_default: bool = False,
    **kwargs,
) -> MusicTrack:
    defaults = dict(
        filename=filename, display_name=display_name,
        file_path=f"/tmp/mediaflow-test/storage/music/{filename}",
        file_size=50000, duration=180.0, format="mp3",
        active=active, is_default=is_default, order=0,
    )
    defaults.update(kwargs)
    return MusicTrack(**defaults)


def make_conversation(title: str = "Test conversation", is_active: bool = True) -> ChatConversation:
    return ChatConversation(title=title, is_active=is_active)


def make_chat_message(
    conversation_id: int,
    role: str = "user",
    content: str = "Hello",
    **kwargs,
) -> ChatMessage:
    defaults = dict(
        conversation_id=conversation_id, role=role, content=content,
    )
    defaults.update(kwargs)
    return ChatMessage(**defaults)
