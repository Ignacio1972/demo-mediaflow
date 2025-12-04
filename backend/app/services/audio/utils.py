"""
Audio Utilities
Shared utility functions for audio processing
"""
import os
import logging
from typing import Dict, Any, Optional
from pydub import AudioSegment

logger = logging.getLogger(__name__)


def get_audio_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract audio metadata using pydub.

    Args:
        file_path: Path to the audio file

    Returns:
        Dictionary with duration, bitrate, sample_rate, and file_size
    """
    try:
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0  # ms to seconds

        # Estimate bitrate from file size and duration
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
