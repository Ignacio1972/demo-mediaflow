"""
Tool executor - executes tools invoked by Claude against MediaFlow services.

Audio generation is delegated to the shared generator module.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.models.category import Category
from app.services.ai.claude import claude_service
from app.services.ai.client_manager import ai_client_manager
from app.services.audio.generator import (
    generate_audio,
    VoiceNotFoundError,
    VoiceInactiveError,
)

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
        """Generate TTS audio via shared generator (commit=False for chat transactions)."""
        text = params["text"]
        voice_id = params.get("voice_id")

        # Default voice resolution (tool-only feature)
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

        try:
            audio_message = await generate_audio(
                text=text,
                voice_id=voice_id,
                db=db,
                add_jingles=params.get("add_jingles", False),
                music_file=params.get("music_file"),
                commit=False,
            )
        except (VoiceNotFoundError, VoiceInactiveError) as e:
            return {"success": False, "message": str(e)}

        audio_url = f"/storage/audio/{audio_message.filename}"

        # Get voice name from snapshot for the response message
        snapshot = json.loads(audio_message.voice_settings_snapshot)
        voice_name = snapshot.get("voice_name", voice_id)

        return {
            "success": True,
            "data": {
                "audio_id": audio_message.id,
                "filename": audio_message.filename,
                "audio_url": audio_url,
                "duration": audio_message.duration,
                "voice_id": audio_message.voice_id,
                "display_name": audio_message.display_name,
            },
            "message": f"Audio generado: {audio_message.duration:.1f}s con voz {voice_name}"
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
