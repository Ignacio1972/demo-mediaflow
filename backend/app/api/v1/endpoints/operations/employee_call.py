"""
Employee/Client Call Operations Endpoints
Handles employee and client call announcement generation
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
    CallType,
    LocationOption,
    EmployeeCallRequest,
    EmployeeCallPreviewRequest,
    EmployeeCallPreviewResponse,
    EmployeeCallResponse,
    EmployeeCallOptionsResponse,
    TemplateInfo,
)
from app.services.tts import voice_manager
from app.services.audio import jingle_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employee-call", tags=["operations-employee-call"])

# ============================================
# Common data for employee call forms
# ============================================

COMMON_LOCATIONS = [
    {"id": "informaciones", "name": "Módulo de Informaciones"},
    {"id": "cajas", "name": "Área de Cajas"},
    {"id": "atencion_cliente", "name": "Atención al Cliente"},
    {"id": "bodega", "name": "Bodega"},
    {"id": "oficina", "name": "Oficina"},
    {"id": "entrada", "name": "Entrada Principal"},
    {"id": "gerencia", "name": "Gerencia"},
    {"id": "rrhh", "name": "Recursos Humanos"},
    {"id": "seguridad", "name": "Seguridad"},
]

CALL_TYPES = [
    {"id": "empleado", "name": "Empleado"},
    {"id": "cliente", "name": "Cliente"},
]

# Default templates (used if no database templates exist)
DEFAULT_TEMPLATES = [
    {
        "id": "employee_call_default",
        "name": "Llamado estándar",
        "description": "Llamado formal con repetición",
        "is_default": True,
        "template_text": "Atención: Se solicita la presencia de {nombre} en {ubicacion}. {nombre}, por favor acérquese a {ubicacion}. Gracias.",
    },
    {
        "id": "employee_call_cliente",
        "name": "Llamado a cliente",
        "description": "Mensaje amable para clientes",
        "is_default": False,
        "template_text": "Estimado cliente {nombre}, por favor diríjase a {ubicacion} donde le están esperando. Gracias.",
    },
    {
        "id": "employee_call_corto",
        "name": "Llamado corto",
        "description": "Mensaje breve y directo",
        "is_default": False,
        "template_text": "{nombre} a {ubicacion}, por favor.",
    },
]


# ============================================
# Endpoints
# ============================================

@router.get(
    "/options",
    response_model=EmployeeCallOptionsResponse,
    summary="Get Form Options",
    description="Get options for the employee call form",
)
async def get_options(db: AsyncSession = Depends(get_db)):
    """
    Get options for employee call form: call types, locations, and templates.
    """
    # Load templates from database
    result = await db.execute(
        select(MessageTemplate)
        .filter(MessageTemplate.module == "employee_call")
        .filter(MessageTemplate.active == True)
        .order_by(MessageTemplate.order.asc())
    )
    db_templates = result.scalars().all()

    # Convert to TemplateInfo format and find default
    templates = []
    default_template_id = None
    default_voice_id = None
    for t in db_templates:
        templates.append({
            "id": t.id,
            "name": t.name,
            "description": t.description or "",
            "is_default": t.is_default
        })
        if t.is_default:
            default_template_id = t.id
            default_voice_id = t.default_voice_id

    # Fallback to hardcoded templates if no database templates exist
    if not templates:
        for t in DEFAULT_TEMPLATES:
            templates.append({
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
                "is_default": t["is_default"]
            })
            if t["is_default"]:
                default_template_id = t["id"]
    elif not default_template_id and templates:
        default_template_id = templates[0]["id"]

    return EmployeeCallOptionsResponse(
        call_types=CALL_TYPES,
        locations=[LocationOption(**loc) for loc in COMMON_LOCATIONS],
        templates=[TemplateInfo(**t) for t in templates],
        default_template_id=default_template_id,
        default_voice_id=default_voice_id
    )


@router.post(
    "/preview",
    response_model=EmployeeCallPreviewResponse,
    summary="Preview Call Text",
    description="Preview the call announcement text",
)
async def preview_text(
    request: EmployeeCallPreviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Preview the call announcement text before generating audio.
    """
    logger.info(
        f"Preview request: {request.call_type} {request.nombre} -> {request.ubicacion}"
    )

    # Try to load template from database
    template_text = None
    use_announcement_sound = False

    result_db = await db.execute(
        select(MessageTemplate).filter(MessageTemplate.id == request.template)
    )
    db_template = result_db.scalar_one_or_none()

    if db_template:
        template_text = db_template.template_text
        use_announcement_sound = db_template.use_announcement_sound
    else:
        # Fallback to hardcoded templates
        for t in DEFAULT_TEMPLATES:
            if t["id"] == request.template:
                template_text = t["template_text"]
                break

        if not template_text:
            # Use default template
            template_text = DEFAULT_TEMPLATES[0]["template_text"]

    # Replace variables in template
    text = template_text.replace("{nombre}", request.nombre)
    text = text.replace("{ubicacion}", request.ubicacion)

    return EmployeeCallPreviewResponse(
        original=text,
        call_type=request.call_type.value,
        nombre=request.nombre,
        ubicacion=request.ubicacion,
        use_announcement_sound=use_announcement_sound
    )


@router.post(
    "/generate",
    response_model=EmployeeCallResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Call Announcement",
    description="Generate TTS audio for an employee/client call announcement",
)
async def generate_call_announcement(
    request: EmployeeCallRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an employee/client call announcement.

    Process:
    1. Get template and replace variables
    2. Generate TTS with ElevenLabs
    3. Add announcement sounds (optional)
    4. Save to database and return audio URL
    """
    try:
        logger.info(
            f"Call announcement request: "
            f"{request.call_type} {request.nombre} -> {request.ubicacion} "
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

        # Try to load template from database
        template_text = None
        use_announcement_sound = False

        result_template = await db.execute(
            select(MessageTemplate).filter(MessageTemplate.id == request.template)
        )
        db_template = result_template.scalar_one_or_none()

        if db_template:
            template_text = db_template.template_text
            use_announcement_sound = db_template.use_announcement_sound
            logger.info(f"Using database template: {db_template.id}")
        else:
            # Fallback to hardcoded templates
            for t in DEFAULT_TEMPLATES:
                if t["id"] == request.template:
                    template_text = t["template_text"]
                    break

            if not template_text:
                template_text = DEFAULT_TEMPLATES[0]["template_text"]

        # Allow request to override template's announcement sound setting
        if request.use_announcement_sound is not None:
            use_announcement_sound = request.use_announcement_sound
            logger.info(f"Request override: use_announcement_sound={use_announcement_sound}")

        # Generate text
        if request.custom_text:
            text = request.custom_text
            logger.info(f"Using custom text: {text[:100]}...")
        else:
            text = template_text.replace("{nombre}", request.nombre)
            text = text.replace("{ubicacion}", request.ubicacion)
            logger.info(f"Generated text: {text[:100]}...")

        # Generate TTS audio
        audio_bytes, voice_used, _ = await voice_manager.generate_with_voice(
            text=text,
            voice_id=request.voice_id,
            db=db,
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_clean = request.nombre.replace(" ", "_").lower()[:20]
        filename = f"call_{timestamp}_{name_clean}_{voice.id}.mp3"
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

        # Add announcement sounds if enabled
        has_announcement = False
        if use_announcement_sound:
            logger.info("Adding announcement sounds (intro + outro)")

            announcement_filename = f"call_ann_{timestamp}_{name_clean}_{voice.id}.mp3"
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

        # Create display name
        type_label = "Empleado" if request.call_type == CallType.EMPLEADO else "Cliente"
        display_name = f"Llamado {type_label}: {request.nombre} a {request.ubicacion}"

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
            has_jingle=False,
            music_file=None,
            status="ready",
            priority=3,  # Normal priority for operations
        )

        db.add(audio_message)
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"Audio message created: ID={audio_message.id}")

        # Build audio URL
        audio_url = f"/storage/audio/{filename}"

        return EmployeeCallResponse(
            success=True,
            text=text,
            audio_url=audio_url,
            audio_id=audio_message.id,
            filename=filename,
            duration=duration,
            voice_id=voice.id,
            voice_name=voice.name,
            call_type=request.call_type.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Call announcement failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando anuncio: {str(e)}"
        )
