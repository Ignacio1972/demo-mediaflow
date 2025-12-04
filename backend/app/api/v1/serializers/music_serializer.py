"""
Music Track Serializer
Converts MusicTrack model to API response format
"""
from app.models.music_track import MusicTrack
from app.schemas.music import MusicTrackResponse


def serialize_music_track(track: MusicTrack) -> MusicTrackResponse:
    """
    Serialize a MusicTrack model to a MusicTrackResponse schema.

    Args:
        track: MusicTrack model instance

    Returns:
        MusicTrackResponse with track data formatted for API response
    """
    return MusicTrackResponse(
        id=track.id,
        filename=track.filename,
        display_name=track.display_name,
        file_size=track.file_size,
        duration=track.duration,
        bitrate=track.bitrate,
        is_default=track.is_default,
        active=track.active,
        order=track.order,
        artist=track.artist,
        genre=track.genre,
        mood=track.mood,
        audio_url=f"/storage/music/{track.filename}",
        created_at=track.created_at.isoformat() if track.created_at else None,
        updated_at=track.updated_at.isoformat() if track.updated_at else None,
    )
