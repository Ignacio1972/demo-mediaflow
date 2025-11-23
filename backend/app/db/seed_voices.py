"""
Seed initial voices to database
Run this script to populate the database with sample voices
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.voice_settings import VoiceSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# REAL voices from legacy system (migrated from /var/www/casa/src/api/data/voices-config.json)
# Voice settings converted from legacy scale (0-1) to v2.1 scale (0-100)
# Legacy TTS config: style=0.5 (50%), stability=0.55 (55%), similarity_boost=0.8 (80%)
# Legacy jingle config: intro_silence=7s, outro_silence=4.5s, music_volume=1.65, voice_volume=2.8
SAMPLE_VOICES = [
    {
        "id": "juan_carlos",
        "name": "Juan Carlos",
        "elevenlabs_id": "G4IAP30yc6c1gK0csDfu",  # REAL ElevenLabs ID from legacy
        "active": True,
        "is_default": True,
        "order": 1,
        "gender": "M",
        "accent": "Neutral Spanish",
        "description": "Professional male voice, default voice from legacy system",
        "style": 50.0,  # Legacy: 0.5 * 100
        "stability": 55.0,  # Legacy: 0.55 * 100
        "similarity_boost": 80.0,  # Legacy: 0.8 * 100
        "use_speaker_boost": True,
        "volume_adjustment": 0.0,  # Legacy: 0 dB
        "jingle_settings": {
            "music_volume": 1.65,  # From legacy jingle-config.json
            "voice_volume": 2.8,
            "duck_level": 0.95,
            "intro_silence": 7,  # Legacy jingle default
            "outro_silence": 4.5,
        },
    },
    {
        "id": "yorman",
        "name": "Mario",
        "elevenlabs_id": "J2Jb9yZNvpXUNAL3a2bw",  # REAL ElevenLabs ID from legacy
        "active": True,
        "is_default": False,
        "order": 2,
        "gender": "M",
        "accent": "Neutral Spanish",
        "description": "Male voice, friendly and clear",
        "style": 50.0,
        "stability": 55.0,
        "similarity_boost": 80.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.5,  # Legacy: +0.5 dB
        "jingle_settings": {
            "music_volume": 1.65,
            "voice_volume": 2.8,
            "duck_level": 0.95,
            "intro_silence": 7,
            "outro_silence": 4.5,
        },
    },
    {
        "id": "veronica",
        "name": "Francisca",
        "elevenlabs_id": "Obg6KIFo8Md4PUo1m2mR",  # REAL ElevenLabs ID from legacy
        "active": True,
        "is_default": False,
        "order": 3,
        "gender": "F",
        "accent": "Spanish",
        "description": "Female voice, energetic and expressive - REQUIRES +7dB boost",
        "style": 50.0,
        "stability": 55.0,
        "similarity_boost": 80.0,
        "use_speaker_boost": True,
        "volume_adjustment": 7.0,  # Legacy: +7 dB - CRITICAL for this voice
        "jingle_settings": {
            "music_volume": 1.65,
            "voice_volume": 2.8,
            "duck_level": 0.95,
            "intro_silence": 7,
            "outro_silence": 4.5,
        },
    },
    {
        "id": "cristian",
        "name": "Jose Miguel",
        "elevenlabs_id": "nNS8uylvF9GBWVSiIt5h",  # REAL ElevenLabs ID from legacy
        "active": True,
        "is_default": False,
        "order": 4,
        "gender": "M",
        "accent": "Spanish",
        "description": "Male voice, young and modern",
        "style": 50.0,
        "stability": 55.0,
        "similarity_boost": 80.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.5,  # Legacy: +0.5 dB
        "jingle_settings": {
            "music_volume": 1.65,
            "voice_volume": 2.8,
            "duck_level": 0.95,
            "intro_silence": 7,
            "outro_silence": 4.5,
        },
    },
    {
        "id": "sandra",
        "name": "Titi",
        "elevenlabs_id": "rEVYTKPqwSMhytFPayIb",  # REAL ElevenLabs ID from legacy
        "active": True,
        "is_default": False,
        "order": 5,
        "gender": "F",
        "accent": "Spanish",
        "description": "Female voice, warm and friendly",
        "style": 50.0,
        "stability": 55.0,
        "similarity_boost": 80.0,
        "use_speaker_boost": True,
        "volume_adjustment": -0.5,  # Legacy: -0.5 dB
        "jingle_settings": {
            "music_volume": 1.65,
            "voice_volume": 2.8,
            "duck_level": 0.95,
            "intro_silence": 7,
            "outro_silence": 4.5,
        },
    },
]


async def seed_voices():
    """Seed voices into database"""
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🌱 Starting voice seeding...")

            for voice_data in SAMPLE_VOICES:
                # Check if voice already exists
                result = await session.execute(
                    select(VoiceSettings).filter(
                        VoiceSettings.id == voice_data["id"]
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"⏭️  Voice '{voice_data['id']}' already exists, skipping")
                    continue

                # Create new voice
                voice = VoiceSettings(**voice_data)
                session.add(voice)
                logger.info(f"✅ Added voice: {voice.name} (id={voice.id})")

            # Commit all voices
            await session.commit()
            logger.info("🎉 Voice seeding completed successfully!")

            # Display summary
            result = await session.execute(select(VoiceSettings))
            all_voices = result.scalars().all()
            logger.info(f"\n📊 Total voices in database: {len(all_voices)}")
            for v in all_voices:
                status = "🟢" if v.active else "🔴"
                default = "⭐" if v.is_default else "  "
                logger.info(
                    f"{status} {default} {v.name} (id={v.id}, order={v.order}, vol_adj={v.volume_adjustment}dB)"
                )

        except Exception as e:
            logger.error(f"❌ Error seeding voices: {str(e)}", exc_info=True)
            await session.rollback()
            raise


async def clear_voices():
    """Clear all voices from database (use with caution!)"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(VoiceSettings))
            voices = result.scalars().all()

            for voice in voices:
                await session.delete(voice)

            await session.commit()
            logger.info(f"🗑️  Deleted {len(voices)} voices from database")

        except Exception as e:
            logger.error(f"❌ Error clearing voices: {str(e)}", exc_info=True)
            await session.rollback()
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        logger.warning("⚠️  Clearing all voices from database...")
        asyncio.run(clear_voices())
    else:
        asyncio.run(seed_voices())
