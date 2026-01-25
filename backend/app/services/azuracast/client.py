"""
AzuraCast API Client for MediaFlow integration.

Handles:
- Uploading audio files to AzuraCast media library
- Sending interrupt commands to Liquidsoap for immediate playback
"""
import base64
import httpx
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of uploading a file to AzuraCast."""
    success: bool
    file_id: Optional[int] = None
    filename: Optional[str] = None
    path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class InterruptResult:
    """Result of sending an interrupt command."""
    success: bool
    request_id: Optional[str] = None
    error: Optional[str] = None


class AzuraCastClient:
    """Client for interacting with AzuraCast API."""

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        station_id: int = None,
        station_name: str = None,
        media_folder: str = None,
    ):
        self.base_url = (base_url or settings.AZURACAST_URL).rstrip("/")
        self.api_key = api_key or settings.AZURACAST_API_KEY
        self.station_id = station_id or settings.AZURACAST_STATION_ID
        self.station_name = station_name or settings.AZURACAST_STATION_NAME
        self.media_folder = media_folder or settings.AZURACAST_MEDIA_FOLDER

        if not self.api_key:
            logger.warning("AzuraCast API key not configured")

    @property
    def headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

    async def check_connection(self) -> bool:
        """Check if AzuraCast is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/station/{self.station_id}/status",
                    headers=self.headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info(
                        f"AzuraCast connected - Backend: {data.get('backendRunning')}, "
                        f"Frontend: {data.get('frontendRunning')}"
                    )
                    return True
                else:
                    logger.error(f"AzuraCast status check failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"AzuraCast connection error: {e}")
            return False

    async def upload_file(
        self,
        file_path: str,
        target_filename: Optional[str] = None,
    ) -> UploadResult:
        """
        Upload an audio file to AzuraCast media library.

        Args:
            file_path: Local path to the audio file
            target_filename: Optional custom filename for the upload

        Returns:
            UploadResult with upload status and file info
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return UploadResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )

            # Use original filename or custom name
            filename = target_filename or path.name
            remote_path = f"{self.media_folder}/{filename}"

            # Read and encode file
            file_content = path.read_bytes()
            base64_content = base64.b64encode(file_content).decode("utf-8")

            logger.info(
                f"Uploading to AzuraCast: {filename} "
                f"({len(file_content)} bytes) -> {remote_path}"
            )

            # Upload via API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/station/{self.station_id}/files",
                    headers={**self.headers, "Content-Type": "application/json"},
                    json={
                        "path": remote_path,
                        "file": base64_content,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Upload successful: ID={data.get('id')}, Path={remote_path}")
                    return UploadResult(
                        success=True,
                        file_id=data.get("id"),
                        filename=filename,
                        path=remote_path,
                    )
                else:
                    error_msg = f"Upload failed: HTTP {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return UploadResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return UploadResult(success=False, error=error_msg)

    async def interrupt_with_file(self, filename: str) -> InterruptResult:
        """
        Interrupt current playback with the specified file.

        This sends a command to Liquidsoap's interrupting_requests queue
        which will immediately play the file, interrupting current audio.

        Args:
            filename: Name of the file in the media folder (not full path)

        Returns:
            InterruptResult with command status
        """
        import asyncio
        import subprocess

        try:
            # Build the file URI for Liquidsoap
            file_uri = (
                f"file:///var/azuracast/stations/{self.station_name}/media/"
                f"{self.media_folder}/{filename}"
            )

            logger.info(f"Sending interrupt command: {file_uri}")

            # Send command via docker exec + socat to liquidsoap socket
            socket_path = f"/var/azuracast/stations/{self.station_name}/config/liquidsoap.sock"
            command = f'interrupting_requests.push {file_uri}'
            docker_cmd = [
                'docker', 'exec', 'azuracast', 'bash', '-c',
                f'echo "{command}" | socat - UNIX-CONNECT:{socket_path}'
            ]

            # Run the command asynchronously
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            output = stdout.decode().strip()
            error_output = stderr.decode().strip()

            if error_output:
                logger.warning(f"Interrupt stderr: {error_output}")

            # Parse output - first line should be request ID
            lines = output.split('\n')
            first_line = lines[0].strip() if lines else ''

            # If numeric, it's a request ID (success)
            if first_line.isdigit():
                logger.info(f"Interrupt command sent successfully: Request ID={first_line}")
                return InterruptResult(success=True, request_id=first_line)

            # Check for explicit errors
            if 'error' in output.lower() or 'failed' in output.lower():
                error_msg = f"Liquidsoap error: {output}"
                logger.error(error_msg)
                return InterruptResult(success=False, error=error_msg)

            # If no error but also no ID, assume success
            logger.info(f"Interrupt command sent (no ID returned): {output}")
            return InterruptResult(success=True, request_id=None)

        except Exception as e:
            error_msg = f"Interrupt error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return InterruptResult(success=False, error=error_msg)

    async def send_audio_to_radio(
        self,
        file_path: str,
        interrupt: bool = True,
        target_filename: Optional[str] = None,
    ) -> dict:
        """
        Complete flow: Upload file to AzuraCast and optionally interrupt radio.

        Args:
            file_path: Local path to the audio file
            interrupt: If True, immediately play the file (interrupts current audio)
            target_filename: Optional custom filename

        Returns:
            Dict with upload and interrupt results
        """
        result = {
            "success": False,
            "upload": None,
            "interrupt": None,
            "message": "",
        }

        # Step 1: Upload file
        upload_result = await self.upload_file(file_path, target_filename)
        result["upload"] = {
            "success": upload_result.success,
            "file_id": upload_result.file_id,
            "filename": upload_result.filename,
            "path": upload_result.path,
            "error": upload_result.error,
        }

        if not upload_result.success:
            result["message"] = f"Upload failed: {upload_result.error}"
            return result

        # Step 2: Send interrupt command (if requested)
        if interrupt:
            interrupt_result = await self.interrupt_with_file(upload_result.filename)
            result["interrupt"] = {
                "success": interrupt_result.success,
                "request_id": interrupt_result.request_id,
                "error": interrupt_result.error,
            }

            if interrupt_result.success:
                result["success"] = True
                result["message"] = "Audio uploaded and playing on radio"
            else:
                result["message"] = f"Uploaded but interrupt failed: {interrupt_result.error}"
        else:
            result["success"] = True
            result["message"] = "Audio uploaded to library (no interrupt)"

        return result

    async def get_now_playing(self) -> Optional[dict]:
        """Get current now playing information."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/nowplaying/{self.station_id}",
                    headers=self.headers,
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting now playing: {e}")
            return None

    async def skip_song(self) -> dict:
        """
        Skip the currently playing song.

        Calls the Azuracast backend action API to skip to the next track.

        Returns:
            Dict with success status and message
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/station/{self.station_id}/backend/skip",
                    headers=self.headers,
                )

                if response.status_code == 200:
                    logger.info("Skip command sent successfully")
                    return {
                        "success": True,
                        "message": "Song skipped successfully"
                    }
                else:
                    error_msg = f"Skip failed: HTTP {response.status_code}"
                    logger.error(f"{error_msg} - {response.text}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "error": response.text
                    }
        except Exception as e:
            error_msg = f"Skip error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg
            }


# Singleton instance
azuracast_client = AzuraCastClient()
