"""
Music Track Settings API Endpoints
Handles music track management for jingle generation - v2.1 Playground
"""
import os
import logging
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.models.music_track import MusicTrack
from app.core.config import settings
from app.schemas.music import (
    MusicTrackResponse,
    MusicTrackUpdate,
    MusicReorderRequest,
)
from app.api.v1.serializers import serialize_music_track
from app.services.audio.utils import get_audio_metadata

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/music",
    response_model=List[MusicTrackResponse],
    summary="Get All Music Tracks",
    description="Get all music tracks for jingle generation",
)
async def get_all_music(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all music tracks ordered by order field"""
    try:
        logger.info("🎵 Fetching all music tracks")

        query = select(MusicTrack).order_by(MusicTrack.order.asc())
        if active_only:
            query = query.filter(MusicTrack.active == True)

        result = await db.execute(query)
        tracks = result.scalars().all()

        logger.info(f"✅ Retrieved {len(tracks)} music tracks")

        return [serialize_music_track(t) for t in tracks]

    except Exception as e:
        logger.error(f"❌ Failed to fetch music: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch music: {str(e)}",
        )


@router.get(
    "/music/{track_id}",
    response_model=MusicTrackResponse,
    summary="Get Single Music Track",
)
async def get_music_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single music track by ID"""
    try:
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        return serialize_music_track(track)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch track: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch track: {str(e)}",
        )


@router.post(
    "/music",
    response_model=MusicTrackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Music Track",
    description="Upload a new music track for jingle generation",
)
async def upload_music(
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    artist: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    mood: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new music track"""
    file_path = None
    try:
        logger.info(f"📤 Uploading music: {file.filename}")

        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided",
            )

        allowed_extensions = {".mp3", ".wav", ".ogg", ".m4a"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
            )

        # Check if filename already exists
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.filename == file.filename)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A track with filename '{file.filename}' already exists",
            )

        # Ensure music directory exists
        os.makedirs(settings.MUSIC_PATH, exist_ok=True)

        # Save file
        file_path = os.path.join(settings.MUSIC_PATH, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"💾 File saved: {file_path}")

        # Get audio metadata
        metadata = get_audio_metadata(file_path)

        # Get next order number
        result = await db.execute(select(MusicTrack))
        all_tracks = result.scalars().all()
        next_order = max([t.order for t in all_tracks], default=-1) + 1

        # Create display name from filename if not provided
        if not display_name:
            display_name = os.path.splitext(file.filename)[0]

        # Create database record
        track = MusicTrack(
            filename=file.filename,
            display_name=display_name,
            file_path=file_path,
            file_size=metadata.get("file_size"),
            duration=metadata.get("duration"),
            bitrate=metadata.get("bitrate"),
            sample_rate=metadata.get("sample_rate"),
            format=file_ext[1:],
            is_default=False,
            active=True,
            order=next_order,
            artist=artist,
            genre=genre,
            mood=mood,
        )

        db.add(track)
        await db.commit()
        await db.refresh(track)

        logger.info(f"✅ Music track created: {track.display_name} (ID={track.id})")

        return serialize_music_track(track)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to upload music: {str(e)}", exc_info=True)
        # Clean up file if it was saved
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload music: {str(e)}",
        )


@router.patch(
    "/music/{track_id}",
    response_model=MusicTrackResponse,
    summary="Update Music Track",
)
async def update_music_track(
    track_id: int,
    update_data: MusicTrackUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update music track metadata"""
    try:
        logger.info(f"📝 Updating music track: {track_id}")

        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(track, field, value)

        await db.commit()
        await db.refresh(track)

        logger.info(f"✅ Music track updated: {track.display_name}")

        return serialize_music_track(track)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update track: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update track: {str(e)}",
        )


@router.delete(
    "/music/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Music Track",
)
async def delete_music_track(
    track_id: int,
    delete_file: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Delete a music track"""
    try:
        logger.info(f"🗑️ Deleting music track: {track_id}")

        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        # Delete file if requested
        if delete_file and track.file_path and os.path.exists(track.file_path):
            os.remove(track.file_path)
            logger.info(f"🗑️ File deleted: {track.file_path}")

        # Delete database record
        await db.delete(track)
        await db.commit()

        logger.info(f"✅ Music track deleted: {track.display_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete track: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete track: {str(e)}",
        )


@router.patch(
    "/music/{track_id}/set-default",
    summary="Set Default Music Track",
)
async def set_default_music(
    track_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Set a music track as the default"""
    try:
        logger.info(f"⭐ Setting default music: {track_id}")

        # Check track exists
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        # Unset all defaults
        await db.execute(
            update(MusicTrack).values(is_default=False)
        )

        # Set new default
        track.is_default = True
        await db.commit()

        logger.info(f"✅ Default music set: {track.display_name}")

        return {"success": True, "message": f"'{track.display_name}' is now the default music"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to set default music: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default music: {str(e)}",
        )


@router.put(
    "/music/reorder",
    summary="Reorder Music Tracks",
)
async def reorder_music(
    request: MusicReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder music tracks"""
    try:
        logger.info(f"🔄 Reordering music tracks: {request.track_ids}")

        for index, track_id in enumerate(request.track_ids):
            await db.execute(
                update(MusicTrack)
                .where(MusicTrack.id == track_id)
                .values(order=index)
            )

        await db.commit()

        logger.info("✅ Music tracks reordered")

        return {"success": True, "message": "Music tracks reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder music: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder music: {str(e)}",
        )
