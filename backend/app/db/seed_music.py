"""
Seed Music Tracks
Populates the music_tracks table with existing music files
"""
import os
import asyncio
import logging
from pydub import AudioSegment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.music_track import MusicTrack
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Music metadata for existing files
MUSIC_METADATA = {
    "Cool.mp3": {
        "display_name": "Cool",
        "genre": "Electronic",
        "mood": "energetic",
    },
    "Kids.mp3": {
        "display_name": "Kids",
        "genre": "Pop",
        "mood": "happy",
    },
    "Pop.mp3": {
        "display_name": "Pop",
        "genre": "Pop",
        "mood": "upbeat",
    },
    "Slow.mp3": {
        "display_name": "Slow",
        "genre": "Ambient",
        "mood": "calm",
    },
    "Smooth.mp3": {
        "display_name": "Smooth",
        "genre": "Jazz",
        "mood": "relaxed",
    },
    "Uplift.mp3": {
        "display_name": "Uplift",
        "genre": "Electronic",
        "mood": "inspiring",
    },
    "_Independencia.mp3": {
        "display_name": "Independencia",
        "genre": "Latin",
        "mood": "festive",
    },
}


def get_audio_metadata(file_path: str) -> dict:
    """Extract audio metadata using pydub"""
    try:
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0  # ms to seconds

        file_size = os.path.getsize(file_path)
        if duration > 0:
            bitrate_kbps = int((file_size * 8) / (duration * 1000))
            bitrate = f"{bitrate_kbps}kbps"
        else:
            bitrate = "unknown"

        return {
            "duration": round(duration, 2),
            "bitrate": bitrate,
            "sample_rate": audio.frame_rate,
            "file_size": file_size,
        }
    except Exception as e:
        logger.warning(f"Could not extract audio metadata: {e}")
        return {
            "duration": None,
            "bitrate": None,
            "sample_rate": None,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else None,
        }


async def seed_music():
    """Seed music tracks from existing files"""
    logger.info("🎵 Starting music seed...")

    async with AsyncSessionLocal() as db:
        # Check if music already exists
        result = await db.execute(select(MusicTrack))
        existing = result.scalars().all()

        if existing:
            logger.info(f"⚠️ Music tracks already exist ({len(existing)} tracks). Skipping seed.")
            return

        # Scan music directory
        music_path = settings.MUSIC_PATH
        if not os.path.exists(music_path):
            logger.error(f"❌ Music directory not found: {music_path}")
            return

        files = [f for f in os.listdir(music_path) if f.endswith(('.mp3', '.wav', '.ogg', '.m4a'))]
        logger.info(f"📁 Found {len(files)} music files")

        for order, filename in enumerate(sorted(files)):
            file_path = os.path.join(music_path, filename)

            # Get metadata
            meta = MUSIC_METADATA.get(filename, {})
            audio_meta = get_audio_metadata(file_path)

            # Create display name from filename if not in metadata
            display_name = meta.get("display_name", os.path.splitext(filename)[0])

            track = MusicTrack(
                filename=filename,
                display_name=display_name,
                file_path=file_path,
                file_size=audio_meta.get("file_size"),
                duration=audio_meta.get("duration"),
                bitrate=audio_meta.get("bitrate"),
                sample_rate=audio_meta.get("sample_rate"),
                format=os.path.splitext(filename)[1][1:],
                is_default=(order == 0),  # First track is default
                active=True,
                order=order,
                genre=meta.get("genre"),
                mood=meta.get("mood"),
            )

            db.add(track)
            logger.info(f"  ✅ Added: {display_name} ({filename})")

        await db.commit()
        logger.info(f"🎉 Music seed completed! Added {len(files)} tracks.")


if __name__ == "__main__":
    asyncio.run(seed_music())
