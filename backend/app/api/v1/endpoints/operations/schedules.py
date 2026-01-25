"""
Schedules Operations Endpoints
Handles opening/closing announcement generation
"""
import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydub import AudioSegment

from app.db.session import get_db
from app.models.voice_settings import VoiceSettings
from app.models.audio import AudioMessage
from app.models.message_template import MessageTemplate
from app.schemas.operations import (
    ScheduleAnnouncementRequest,
    ScheduleAnnouncementResponse,
    SchedulePreviewRequest,
    SchedulePreviewResponse,
    ScheduleOptionsResponse,
    ScheduleType,
    ScheduleVariant,
    MinutesOption,
)
from app.services.tts import voice_manager
from app.services.audio import jingle_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedules", tags=["operations-schedules"])

# ============================================
# Message Templates (Hardcoded Fallback)
# ============================================

# Template ID mapping: (type, variant) -> template_id
# Only closing variants are supported
TEMPLATE_ID_MAP = {
    (ScheduleType.CLOSING, ScheduleVariant.NORMAL): "schedules_cierre_normal",
    (ScheduleType.CLOSING, ScheduleVariant.IN_MINUTES): "schedules_cierre_minutos",
    (ScheduleType.CLOSING, ScheduleVariant.IMMEDIATE): "schedules_cierre_inmediato",
}

# Hardcoded fallback templates (used if not in database)
# Only closing templates
SCHEDULE_TEMPLATES = {
    "schedules_cierre_normal": (
        "Estimados clientes, les informamos que el establecimiento "
        "cerrará pronto. Por favor diríjanse a las cajas para realizar sus compras."
    ),
    "schedules_cierre_minutos": (
        "Estimados clientes, les recordamos que el establecimiento "
        "cerrará en {minutes} minutos. Por favor diríjanse a las cajas."
    ),
    "schedules_cierre_inmediato": (
        "Estimados clientes, el establecimiento ha cerrado. "
        "Gracias por su visita, los esperamos pronto."
    ),
}

# Form options (only closing)
SCHEDULE_TYPES = [
    {"id": "closing", "name": "Cierre"},
]

SCHEDULE_VARIANTS = [
    {
        "id": "normal",
        "name": "Normal",
        "description": "Mensaje estándar de apertura o cierre"
    },
    {
        "id": "in_minutes",
        "name": "En X minutos",
        "description": "Aviso de cierre con tiempo específico"
    },
    {
        "id": "immediate",
        "name": "Inmediato",
        "description": "Ya abierto o ya cerrado"
    },
]

MINUTES_OPTIONS = [
    {"value": 5, "label": "5 minutos"},
    {"value": 10, "label": "10 minutos"},
    {"value": 15, "label": "15 minutos"},
    {"value": 20, "label": "20 minutos"},
    {"value": 30, "label": "30 minutos"},
]


def get_template_id(
    schedule_type: ScheduleType,
    variant: ScheduleVariant
) -> str:
    """Get template ID based on type and variant."""
    return TEMPLATE_ID_MAP.get(
        (schedule_type, variant),
        TEMPLATE_ID_MAP[(ScheduleType.CLOSING, ScheduleVariant.NORMAL)]
    )


async def get_announcement_text(
    schedule_type: ScheduleType,
    variant: ScheduleVariant,
    minutes: int | None,
    db: AsyncSession
) -> tuple[str, str, bool]:
    """
    Get the announcement text based on type and variant.
    Returns tuple of (text, template_id_used, use_announcement_sound).
    First tries database, then falls back to hardcoded.
    """
    template_id = get_template_id(schedule_type, variant)
    use_announcement_sound = False

    # Try to load from database
    result = await db.execute(
        select(MessageTemplate).filter(
            MessageTemplate.id == template_id,
            MessageTemplate.active == True
        )
    )
    db_template = result.scalar_one_or_none()

    if db_template:
        template_text = db_template.template_text
        use_announcement_sound = db_template.use_announcement_sound
        logger.info(f"Using database template: {template_id} (announcement_sound={use_announcement_sound})")
    else:
        # Fallback to hardcoded
        template_text = SCHEDULE_TEMPLATES.get(template_id)
        if not template_text:
            # Final fallback to normal variant
            fallback_id = get_template_id(schedule_type, ScheduleVariant.NORMAL)
            template_text = SCHEDULE_TEMPLATES.get(fallback_id, "")
            template_id = fallback_id
        logger.info(f"Using hardcoded template: {template_id}")

    if not template_text:
        raise ValueError(f"No template found for {schedule_type}/{variant}")

    # Replace minutes placeholder if present
    if "{minutes}" in template_text:
        if minutes:
            template_text = template_text.replace("{minutes}", str(minutes))
        else:
            template_text = template_text.replace("{minutes}", "15")  # Default

    return template_text, template_id, use_announcement_sound


# ============================================
# Endpoints
# ============================================

@router.get(
    "/options",
    response_model=ScheduleOptionsResponse,
    summary="Get Form Options",
    description="Get options for the schedule announcement form",
)
async def get_options():
    """Get options for the schedule form: types, variants, and minutes."""
    return ScheduleOptionsResponse(
        types=SCHEDULE_TYPES,
        variants=SCHEDULE_VARIANTS,
        minutes_options=[MinutesOption(**m) for m in MINUTES_OPTIONS]
    )


@router.post(
    "/preview",
    response_model=SchedulePreviewResponse,
    summary="Preview Announcement Text",
    description="Preview the announcement text before generating audio",
)
async def preview_text(
    request: SchedulePreviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """Preview the announcement text based on selected options."""
    logger.info(
        f"Schedule preview: type={request.schedule_type} "
        f"variant={request.variant} minutes={request.minutes}"
    )

    text, _, use_announcement_sound = await get_announcement_text(
        schedule_type=request.schedule_type,
        variant=request.variant,
        minutes=request.minutes,
        db=db
    )

    return SchedulePreviewResponse(
        text=text,
        schedule_type=request.schedule_type.value,
        variant=request.variant.value,
        minutes=request.minutes,
        use_announcement_sound=use_announcement_sound
    )


@router.post(
    "/generate",
    response_model=ScheduleAnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Schedule Announcement",
    description="Generate TTS audio for an opening/closing announcement",
)
async def generate_schedule_announcement(
    request: ScheduleAnnouncementRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a schedule announcement audio.

    Process:
    1. Get announcement text from template
    2. Generate TTS with ElevenLabs
    3. Mix with background music (optional)
    4. Save to database and return audio URL
    """
    try:
        logger.info(
            f"Schedule announcement request: "
            f"type={request.schedule_type} variant={request.variant} "
            f"voice={request.voice_id}"
        )

        # Get voice configuration
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == request.voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            logger.warning(f"Voice not found: {request.voice_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voz '{request.voice_id}' no encontrada"
            )

        if not voice.active:
            logger.warning(f"Voice inactive: {request.voice_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voz '{request.voice_id}' está inactiva"
            )

        # Get announcement text
        text, template_id_used, use_announcement_sound = await get_announcement_text(
            schedule_type=request.schedule_type,
            variant=request.variant,
            minutes=request.minutes,
            db=db
        )

        # Allow request to override template's announcement sound setting
        if request.use_announcement_sound is not None:
            use_announcement_sound = request.use_announcement_sound
            logger.info(f"Request override: use_announcement_sound={use_announcement_sound}")

        logger.info(f"Announcement text: {text[:100]}... (template: {template_id_used}, announcement={use_announcement_sound})")

        # Generate TTS audio
        audio_bytes, voice_used, _ = await voice_manager.generate_with_voice(
            text=text,
            voice_id=request.voice_id,
            db=db,
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        type_short = "open" if request.schedule_type == ScheduleType.OPENING else "close"
        filename = f"schedule_{type_short}_{timestamp}_{voice.id}.mp3"
        file_path = os.path.join(settings.AUDIO_PATH, filename)

        # Ensure directory exists
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        # Save audio file
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"TTS audio saved: {filename}")

        # Get audio metadata
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0
        file_size = os.path.getsize(file_path)

        # Apply volume adjustment if configured
        if voice.volume_adjustment != 0:
            logger.info(f"Applying volume adjustment: {voice.volume_adjustment} dB")
            adjusted_audio = audio + voice.volume_adjustment
            adjusted_audio.export(file_path, format="mp3", bitrate="192k")
            file_size = os.path.getsize(file_path)

        # Add announcement sounds if template has it enabled
        has_jingle = False
        has_announcement = False
        if use_announcement_sound:
            logger.info("Adding announcement sounds (intro + outro)")

            announcement_filename = f"schedule_ann_{type_short}_{timestamp}_{voice.id}.mp3"
            announcement_path = os.path.join(settings.AUDIO_PATH, announcement_filename)

            announcement_result = await jingle_service.add_announcement_sounds(
                voice_audio_path=file_path,
                output_path=announcement_path,
            )

            if announcement_result["success"]:
                os.remove(file_path)
                filename = announcement_filename
                file_path = announcement_path
                duration = announcement_result["duration"]
                file_size = os.path.getsize(file_path)
                has_announcement = True
                logger.info(f"Announcement audio created: {filename}")
            else:
                logger.warning(f"Announcement sounds failed: {announcement_result.get('error')}")

        # Mix with background music if requested (only if no announcement sounds)
        elif request.music_file:
            logger.info(f"Creating jingle with music: {request.music_file}")

            jingle_filename = f"schedule_jingle_{type_short}_{timestamp}_{voice.id}.mp3"
            jingle_path = os.path.join(settings.AUDIO_PATH, jingle_filename)

            voice_jingle_settings = voice.jingle_settings if voice.jingle_settings else None

            jingle_result = await jingle_service.create_jingle(
                voice_audio_path=file_path,
                music_filename=request.music_file,
                output_path=jingle_path,
                voice_jingle_settings=voice_jingle_settings
            )

            if jingle_result["success"]:
                os.remove(file_path)
                filename = jingle_filename
                file_path = jingle_path
                duration = jingle_result["duration"]
                file_size = os.path.getsize(file_path)
                has_jingle = True
                logger.info(f"Jingle created: {filename}")
            else:
                logger.warning(f"Jingle failed: {jingle_result.get('error')}")

        # Create display name
        type_display = "Apertura" if request.schedule_type == ScheduleType.OPENING else "Cierre"
        variant_display = {
            ScheduleVariant.NORMAL: "",
            ScheduleVariant.IN_MINUTES: f" ({request.minutes} min)",
            ScheduleVariant.IMMEDIATE: " (inmediato)",
        }.get(request.variant, "")
        display_name = f"Horario {type_display}{variant_display}"

        # Get settings snapshot
        settings_snapshot = voice_manager.get_voice_settings_snapshot(voice)

        # Save to database
        audio_message = AudioMessage(
            filename=filename,
            display_name=display_name,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            format="mp3",
            original_text=text,
            voice_id=voice.id,
            voice_settings_snapshot=settings_snapshot,
            volume_adjustment=voice.volume_adjustment,
            has_jingle=has_jingle,
            music_file=request.music_file,
            status="ready",
            priority=3,  # Normal priority for operations
        )

        db.add(audio_message)
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"Audio message created: ID={audio_message.id}")

        # Build audio URL
        audio_url = f"/storage/audio/{filename}"

        return ScheduleAnnouncementResponse(
            success=True,
            text=text,
            audio_url=audio_url,
            audio_id=audio_message.id,
            filename=filename,
            duration=duration,
            voice_id=voice.id,
            voice_name=voice.name,
            schedule_type=request.schedule_type.value,
            variant=request.variant.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schedule announcement failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando anuncio: {str(e)}"
        )
