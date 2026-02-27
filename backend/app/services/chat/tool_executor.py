"""
Tool executor - executes tools invoked by Claude against MediaFlow services.

Replicates audio generation logic from audio.py inline (no generator.py extraction)
to avoid touching existing endpoints.
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydub import AudioSegment

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.models.category import Category
from app.services.ai.claude import claude_service
from app.services.ai.client_manager import ai_client_manager
from app.services.tts import voice_manager
from app.services.audio import jingle_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes chat assistant tools against MediaFlow services"""

    async def execute(self, tool_name: str, tool_input: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Execute a tool. Returns {success, data, message}."""
        handler = getattr(self, f"_tool_{tool_name}", None)
        if not handler:
            return {"success": False, "message": f"Herramienta desconocida: {tool_name}"}
        try:
            return await handler(tool_input, db)
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}

    async def _tool_generate_text_suggestions(self, params: Dict, db: AsyncSession) -> Dict:
        active_client = await ai_client_manager.get_active_client(db)
        client_context = active_client.context if active_client else None

        suggestions = await claude_service.generate_announcements(
            context=params["context"],
            tone=params.get("tone", "profesional"),
            duration=params.get("duration", 10),
            client_context=client_context,
        )
        return {
            "success": True,
            "data": suggestions,
            "message": f"Se generaron {len(suggestions)} sugerencias de texto."
        }

    async def _tool_generate_audio(self, params: Dict, db: AsyncSession) -> Dict:
        """
        Generate TTS audio - replicates logic from audio.py endpoint.
        Uses db.flush() instead of commit (transaction managed by ChatService).
        """
        text = params["text"]
        voice_id = params.get("voice_id")

        # Get default voice if not specified
        if not voice_id:
            result = await db.execute(
                select(VoiceSettings).filter(
                    VoiceSettings.is_default == True, VoiceSettings.active == True
                )
            )
            default_voice = result.scalar_one_or_none()
            if not default_voice:
                result = await db.execute(
                    select(VoiceSettings).filter(VoiceSettings.active == True).limit(1)
                )
                default_voice = result.scalar_one_or_none()
            if not default_voice:
                return {"success": False, "message": "No hay voces configuradas"}
            voice_id = default_voice.id

        # Look up voice settings
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()
        if not voice:
            return {"success": False, "message": f"Voz '{voice_id}' no encontrada"}
        if not voice.active:
            return {"success": False, "message": f"Voz '{voice_id}' está inactiva"}

        add_jingles = params.get("add_jingles", False)
        music_file = params.get("music_file")

        # Generate TTS with automatic voice settings
        audio_bytes, voice_used, effective_settings = await voice_manager.generate_with_voice(
            text=text, voice_id=voice_id, db=db,
        )

        # Generate filename and save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{timestamp}_{voice.id}.mp3"
        file_path = os.path.join(settings.AUDIO_PATH, filename)
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Get audio metadata
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0
        file_size = os.path.getsize(file_path)

        # Apply volume adjustment if configured
        volume_adj = effective_settings.get("volume_adjustment", voice.volume_adjustment)
        if volume_adj != 0:
            adjusted_audio = audio + volume_adj
            adjusted_audio.export(file_path, format="mp3", bitrate="192k")
            file_size = os.path.getsize(file_path)

        # Apply TTS silence padding if NOT using jingle
        if not (add_jingles and music_file):
            tts_settings = voice.tts_settings or {}
            intro_silence = tts_settings.get('intro_silence', 0)
            outro_silence = tts_settings.get('outro_silence', 0)
            if intro_silence > 0 or outro_silence > 0:
                audio = AudioSegment.from_file(file_path)
                if intro_silence > 0:
                    audio = AudioSegment.silent(duration=int(intro_silence * 1000)) + audio
                if outro_silence > 0:
                    audio = audio + AudioSegment.silent(duration=int(outro_silence * 1000))
                audio.export(file_path, format="mp3", bitrate="192k")
                duration = len(audio) / 1000.0
                file_size = os.path.getsize(file_path)

        # Create jingle if requested
        if add_jingles and music_file:
            jingle_filename = f"jingle_{timestamp}_{voice.id}.mp3"
            jingle_path = os.path.join(settings.AUDIO_PATH, jingle_filename)
            voice_jingle_settings = voice.jingle_settings if voice.jingle_settings else None

            jingle_result = await jingle_service.create_jingle(
                voice_audio_path=file_path,
                music_filename=music_file,
                output_path=jingle_path,
                voice_jingle_settings=voice_jingle_settings,
            )

            if jingle_result['success']:
                os.remove(file_path)
                filename = jingle_filename
                file_path = jingle_path
                duration = jingle_result['duration']
                file_size = os.path.getsize(file_path)

        # Create display name
        display_name = text[:50] + "..." if len(text) > 50 else text

        # Get settings snapshot
        settings_snapshot = voice_manager.get_voice_settings_snapshot(voice)

        # Save to database (flush, not commit)
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
            volume_adjustment=effective_settings.get("volume_adjustment", voice.volume_adjustment),
            has_jingle=add_jingles,
            music_file=music_file,
            status="ready",
        )
        db.add(audio_message)
        await db.flush()

        audio_url = f"/storage/audio/{filename}"

        return {
            "success": True,
            "data": {
                "audio_id": audio_message.id,
                "filename": filename,
                "audio_url": audio_url,
                "duration": duration,
                "voice_id": voice.id,
                "display_name": display_name,
            },
            "message": f"Audio generado: {duration:.1f}s con voz {voice.name}"
        }

    async def _tool_list_voices(self, params: Dict, db: AsyncSession) -> Dict:
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.active == True).order_by(VoiceSettings.name)
        )
        voices = result.scalars().all()
        voice_list = [
            {"id": v.id, "name": v.name, "is_default": v.is_default}
            for v in voices
        ]
        return {
            "success": True, "data": voice_list,
            "message": f"Hay {len(voice_list)} voces: {', '.join(v['name'] for v in voice_list)}"
        }

    async def _tool_list_music_tracks(self, params: Dict, db: AsyncSession) -> Dict:
        from app.models.music_track import MusicTrack
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.active == True).order_by(MusicTrack.display_name)
        )
        tracks = result.scalars().all()
        track_list = [
            {"filename": t.filename, "display_name": t.display_name,
             "duration": t.duration, "is_default": t.is_default}
            for t in tracks
        ]
        return {"success": True, "data": track_list,
                "message": f"Hay {len(track_list)} pistas de música disponibles."}

    async def _tool_save_to_library(self, params: Dict, db: AsyncSession) -> Dict:
        audio_id = params["audio_id"]
        result = await db.execute(select(AudioMessage).filter(AudioMessage.id == audio_id))
        audio = result.scalar_one_or_none()
        if not audio:
            return {"success": False, "message": f"Audio #{audio_id} no encontrado"}

        audio.is_favorite = True
        if params.get("display_name"):
            audio.display_name = params["display_name"]
        if params.get("category_id"):
            audio.category_id = params["category_id"]
        await db.flush()

        return {"success": True,
                "data": {"audio_id": audio_id, "display_name": audio.display_name},
                "message": f"Audio '{audio.display_name}' guardado en biblioteca."}

    async def _tool_create_schedule(self, params: Dict, db: AsyncSession) -> Dict:
        from app.models.schedule import Schedule

        audio_id = params["audio_id"]
        schedule_type = params["schedule_type"]

        result = await db.execute(select(AudioMessage).filter(AudioMessage.id == audio_id))
        audio = result.scalar_one_or_none()
        if not audio:
            return {"success": False, "message": f"Audio #{audio_id} no encontrado"}

        schedule = Schedule(
            audio_message_id=audio_id,
            schedule_type=schedule_type,
            active=True,
            start_date=datetime.fromisoformat(params["start_date"]) if params.get("start_date") else datetime.now(),
        )

        if params.get("end_date"):
            schedule.end_date = datetime.fromisoformat(params["end_date"])
        if schedule_type == "interval":
            schedule.interval_minutes = params.get("interval_minutes", 60)
        elif schedule_type == "specific":
            schedule.specific_times = params.get("specific_times", [])
            schedule.days_of_week = params.get("days_of_week", [0, 1, 2, 3, 4, 5, 6])

        db.add(schedule)
        await db.flush()

        return {"success": True,
                "data": {"schedule_id": schedule.id, "schedule_type": schedule_type},
                "message": f"Audio '{audio.display_name}' programado ({schedule_type})."}

    async def _tool_list_schedules(self, params: Dict, db: AsyncSession) -> Dict:
        from app.models.schedule import Schedule
        query = select(Schedule)
        if params.get("active_only", True):
            query = query.filter(Schedule.active == True)
        result = await db.execute(query.order_by(Schedule.created_at.desc()).limit(20))
        schedules = result.scalars().all()

        return {"success": True,
                "data": [
                    {"id": s.id, "audio_message_id": s.audio_message_id,
                     "schedule_type": s.schedule_type, "active": s.active,
                     "next_execution_at": s.next_execution_at.isoformat() if s.next_execution_at else None}
                    for s in schedules
                ],
                "message": f"Hay {len(schedules)} programaciones."}

    async def _tool_list_categories(self, params: Dict, db: AsyncSession) -> Dict:
        result = await db.execute(
            select(Category).filter(Category.active == True).order_by(Category.order)
        )
        categories = result.scalars().all()
        cat_list = [{"id": c.id, "name": c.name, "icon": c.icon, "color": c.color} for c in categories]
        return {"success": True, "data": cat_list,
                "message": f"Hay {len(cat_list)} categorías: {', '.join(c['name'] for c in cat_list)}"}

    async def _tool_search_library(self, params: Dict, db: AsyncSession) -> Dict:
        query = select(AudioMessage).filter(
            AudioMessage.is_favorite == True, AudioMessage.status != "deleted"
        )
        if params.get("query"):
            search = f"%{params['query']}%"
            query = query.filter(
                AudioMessage.display_name.ilike(search) | AudioMessage.original_text.ilike(search)
            )
        if params.get("category_id"):
            query = query.filter(AudioMessage.category_id == params["category_id"])

        limit = min(params.get("limit", 10), 20)
        result = await db.execute(query.order_by(AudioMessage.created_at.desc()).limit(limit))
        messages = result.scalars().all()

        return {"success": True,
                "data": [
                    {"id": m.id, "display_name": m.display_name, "duration": m.duration,
                     "voice_id": m.voice_id, "audio_url": f"/storage/audio/{m.filename}",
                     "created_at": m.created_at.isoformat() if m.created_at else None}
                    for m in messages
                ],
                "message": f"Se encontraron {len(messages)} audios."}

    async def _tool_send_to_radio(self, params: Dict, db: AsyncSession) -> Dict:
        audio_id = params["audio_id"]
        result = await db.execute(select(AudioMessage).filter(AudioMessage.id == audio_id))
        audio = result.scalar_one_or_none()
        if not audio:
            return {"success": False, "message": f"Audio #{audio_id} no encontrado"}

        from app.services.azuracast.client import azuracast_client
        radio_result = await azuracast_client.send_audio_to_radio(audio.file_path)

        if radio_result.get("success"):
            audio.sent_to_player = True
            await db.flush()

        return {
            "success": radio_result.get("success", False),
            "data": {"audio_id": audio_id},
            "message": f"Audio '{audio.display_name}' enviado a la radio." if radio_result.get("success") else "Error enviando a la radio."
        }


tool_executor = ToolExecutor()
