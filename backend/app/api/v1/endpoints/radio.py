"""
Radio/Azuracast control endpoints.

Provides API endpoints to control the Azuracast radio station.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.azuracast.client import azuracast_client

router = APIRouter()


class RadioActionResponse(BaseModel):
    """Response model for radio actions."""
    success: bool
    message: str
    error: str | None = None


class NowPlayingResponse(BaseModel):
    """Response model for now playing info."""
    success: bool
    data: dict | None = None
    error: str | None = None


@router.post("/skip", response_model=RadioActionResponse)
async def skip_song():
    """
    Skip the currently playing song on the radio.

    Sends a skip command to the Azuracast backend (Liquidsoap)
    to advance to the next track in the queue.
    """
    result = await azuracast_client.skip_song()

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("message", "Failed to skip song")
        )

    return RadioActionResponse(
        success=True,
        message=result["message"]
    )


@router.get("/now-playing", response_model=NowPlayingResponse)
async def get_now_playing():
    """
    Get the currently playing song information.

    Returns the now playing data from Azuracast including
    song title, artist, album art, elapsed time, etc.
    """
    data = await azuracast_client.get_now_playing()

    if data is None:
        return NowPlayingResponse(
            success=False,
            error="Could not fetch now playing info"
        )

    return NowPlayingResponse(
        success=True,
        data=data
    )


@router.get("/status")
async def get_radio_status():
    """
    Check if the radio backend is online and accessible.
    """
    is_connected = await azuracast_client.check_connection()

    return {
        "success": is_connected,
        "status": "online" if is_connected else "offline",
        "message": "Radio backend is running" if is_connected else "Radio backend is not accessible"
    }
