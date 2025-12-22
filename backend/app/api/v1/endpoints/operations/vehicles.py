"""
Vehicles Operations Endpoints
Handles vehicle announcement generation with text normalization for TTS
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
    VehicleAnnouncementRequest,
    VehicleAnnouncementResponse,
    TextPreviewRequest,
    TextPreviewResponse,
    PlateValidationRequest,
    PlateValidationResponse,
    TemplatesResponse,
    TemplateInfo,
    OperationsOptionsResponse,
    VehicleBrand,
    VehicleColor,
    PlateInfo,
    AnnouncementComponents,
)
from app.services.text import text_normalizer
from app.services.tts import voice_manager
from app.services.audio import jingle_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicles", tags=["operations-vehicles"])

# ============================================
# Common data for vehicle forms
# ============================================

COMMON_BRANDS = [
    {"id": "toyota", "name": "Toyota"},
    {"id": "chevrolet", "name": "Chevrolet", "tts_name": "Chévrolet"},
    {"id": "nissan", "name": "Nissan", "tts_name": "Níssan"},
    {"id": "hyundai", "name": "Hyundai", "tts_name": "Hiúndai"},
    {"id": "kia", "name": "Kia", "tts_name": "Kía"},
    {"id": "mazda", "name": "Mazda", "tts_name": "Mázda"},
    {"id": "suzuki", "name": "Suzuki", "tts_name": "Suzúki"},
    {"id": "ford", "name": "Ford"},
    {"id": "volkswagen", "name": "Volkswagen"},
    {"id": "honda", "name": "Honda", "tts_name": "Hónda"},
    {"id": "mitsubishi", "name": "Mitsubishi", "tts_name": "Mitsubíshi"},
    {"id": "subaru", "name": "Subaru", "tts_name": "Subarú"},
    {"id": "peugeot", "name": "Peugeot"},
    {"id": "renault", "name": "Renault"},
    {"id": "fiat", "name": "Fiat", "tts_name": "Fíat"},
    {"id": "jeep", "name": "Jeep"},
    {"id": "mercedes", "name": "Mercedes-Benz"},
    {"id": "bmw", "name": "BMW"},
    {"id": "audi", "name": "Audi"},
    {"id": "otro", "name": "Otro"},
]

COMMON_COLORS = [
    {"id": "blanco", "name": "Blanco", "hex_color": "#FFFFFF"},
    {"id": "negro", "name": "Negro", "hex_color": "#000000"},
    {"id": "gris", "name": "Gris", "hex_color": "#808080"},
    {"id": "plata", "name": "Plata", "hex_color": "#C0C0C0"},
    {"id": "rojo", "name": "Rojo", "hex_color": "#FF0000"},
    {"id": "azul", "name": "Azul", "hex_color": "#0000FF"},
    {"id": "verde", "name": "Verde", "hex_color": "#008000"},
    {"id": "amarillo", "name": "Amarillo", "hex_color": "#FFFF00"},
    {"id": "cafe", "name": "Café", "hex_color": "#8B4513"},
    {"id": "beige", "name": "Beige", "hex_color": "#F5F5DC"},
    {"id": "naranja", "name": "Naranja", "hex_color": "#FFA500"},
    {"id": "celeste", "name": "Celeste", "hex_color": "#87CEEB"},
    {"id": "morado", "name": "Morado", "hex_color": "#800080"},
    {"id": "dorado", "name": "Dorado", "hex_color": "#FFD700"},
]


# ============================================
# Endpoints
# ============================================

@router.get(
    "/options",
    response_model=OperationsOptionsResponse,
    summary="Get Form Options",
    description="Get common options for the vehicle announcement form",
)
async def get_options(db: AsyncSession = Depends(get_db)):
    """
    Get common options for vehicle form: brands, colors, and templates.

    Returns predefined lists for dropdowns/autocomplete in the frontend.
    Templates are loaded from the database for the 'vehicles' module.
    """
    # Load templates from database
    result = await db.execute(
        select(MessageTemplate)
        .filter(MessageTemplate.module == "vehicles")
        .filter(MessageTemplate.active == True)
        .order_by(MessageTemplate.order.asc())
    )
    db_templates = result.scalars().all()

    # Convert to TemplateInfo format
    templates = []
    for t in db_templates:
        templates.append({
            "id": t.id,
            "name": t.name,
            "description": t.description or ""
        })

    # Fallback to hardcoded templates if no database templates exist
    if not templates:
        templates = text_normalizer.get_available_templates()

    return OperationsOptionsResponse(
        brands=[VehicleBrand(**b) for b in COMMON_BRANDS],
        colors=[VehicleColor(**c) for c in COMMON_COLORS],
        templates=[TemplateInfo(**t) for t in templates]
    )


@router.get(
    "/templates",
    response_model=TemplatesResponse,
    summary="Get Announcement Templates",
    description="Get available announcement templates",
)
async def get_templates():
    """Get list of available message templates."""
    templates = text_normalizer.get_available_templates()
    return TemplatesResponse(
        templates=[TemplateInfo(**t) for t in templates]
    )


@router.post(
    "/validate-plate",
    response_model=PlateValidationResponse,
    summary="Validate License Plate",
    description="Validate and preview pronunciation of a Chilean license plate",
)
async def validate_plate(request: PlateValidationRequest):
    """
    Validate a license plate format and show how it will be pronounced.

    Supports:
    - New format (2007+): XXXX-YY (4 letters + 2 digits)
    - Old format: XX-YYYY (2 letters + 4 digits)
    """
    logger.info(f"Validating plate: {request.patente}")

    validation = text_normalizer.validate_plate_format(request.patente)
    pronunciation = text_normalizer.normalize_plate(request.patente)

    return PlateValidationResponse(
        valid=validation.get("valid", False),
        format=validation.get("format"),
        letters=validation.get("letters"),
        numbers=validation.get("numbers"),
        normalized=validation.get("normalized"),
        pronunciation=pronunciation,
        warning=validation.get("warning"),
        error=validation.get("error"),
    )


@router.post(
    "/preview",
    response_model=TextPreviewResponse,
    summary="Preview Normalized Text",
    description="Preview the announcement text with normalized plate pronunciation",
)
async def preview_text(
    request: TextPreviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Preview how the announcement will sound before generating audio.

    Shows both original and normalized text so user can verify
    the plate pronunciation is correct.
    """
    logger.info(
        f"Text preview: {request.marca} {request.color} {request.patente}"
    )

    # Try to load template from database
    custom_template_text = None
    result_db = await db.execute(
        select(MessageTemplate).filter(MessageTemplate.id == request.template)
    )
    db_template = result_db.scalar_one_or_none()
    if db_template:
        custom_template_text = db_template.template_text

    result = text_normalizer.normalize_vehicle_announcement(
        marca=request.marca,
        color=request.color,
        patente=request.patente,
        template=request.template,
        number_mode=request.number_mode.value,
        custom_template_text=custom_template_text
    )

    return TextPreviewResponse(
        original=result["original"],
        normalized=result["normalized"],
        plate_info=PlateInfo(**result["plate_info"]),
        components=AnnouncementComponents(**result["components"])
    )


@router.post(
    "/generate",
    response_model=VehicleAnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Vehicle Announcement",
    description="Generate TTS audio for a vehicle announcement with normalized text",
)
async def generate_vehicle_announcement(
    request: VehicleAnnouncementRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a vehicle announcement with automatic text normalization.

    Process:
    1. Normalize text (plate letters and numbers)
    2. Generate TTS with ElevenLabs
    3. Mix with background music (optional)
    4. Save to database and return audio URL
    """
    try:
        logger.info(
            f"Vehicle announcement request: "
            f"{request.marca} {request.color} {request.patente} "
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
                detail=f"Voz '{request.voice_id}' esta inactiva"
            )

        # Try to load template from database
        custom_template_text = None
        result_template = await db.execute(
            select(MessageTemplate).filter(MessageTemplate.id == request.template)
        )
        db_template = result_template.scalar_one_or_none()
        if db_template:
            custom_template_text = db_template.template_text
            logger.info(f"Using database template: {db_template.id}")

        # Normalize text
        normalized_result = text_normalizer.normalize_vehicle_announcement(
            marca=request.marca,
            color=request.color,
            patente=request.patente,
            template=request.template,
            number_mode=request.number_mode.value,
            custom_template_text=custom_template_text
        )

        original_text = normalized_result["original"]
        normalized_text = normalized_result["normalized"]
        plate_info = normalized_result["plate_info"]

        logger.info(f"Normalized text: {normalized_text[:100]}...")

        # Generate TTS audio with the normalized text
        audio_bytes, voice_used = await voice_manager.generate_with_voice(
            text=normalized_text,
            voice_id=request.voice_id,
            db=db,
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plate_clean = request.patente.replace("-", "").replace(" ", "").upper()
        filename = f"vehicle_{timestamp}_{plate_clean}_{voice.id}.mp3"
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

        # Mix with background music if requested
        has_jingle = False
        if request.music_file:
            logger.info(f"Creating jingle with music: {request.music_file}")

            jingle_filename = f"vehicle_jingle_{timestamp}_{plate_clean}_{voice.id}.mp3"
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
        display_name = f"Vehiculo {request.marca} {request.color} - {request.patente.upper()}"

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
            original_text=original_text,
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

        return VehicleAnnouncementResponse(
            success=True,
            original_text=original_text,
            normalized_text=normalized_text,
            audio_url=audio_url,
            audio_id=audio_message.id,
            filename=filename,
            duration=duration,
            voice_id=voice.id,
            voice_name=voice.name,
            template_used=request.template,
            plate_info=PlateInfo(**plate_info),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vehicle announcement failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando anuncio: {str(e)}"
        )
