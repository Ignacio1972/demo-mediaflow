"""
Jingle Service - Mixes TTS audio with background music
Based on legacy jingle-service.php logic, adapted for Python/FastAPI
"""
import os
import logging
import subprocess
import tempfile
import shutil
from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class JingleConfig:
    """Configuration for jingle generation"""
    music_volume: float = 1.65      # Music volume multiplier
    voice_volume: float = 2.8       # Voice volume multiplier
    fade_in: float = 1.5            # Fade in duration (seconds)
    fade_out: float = 4.5           # Fade out duration (seconds)
    duck_level: float = 0.95        # Ducking level (0.0-1.0, higher = more ducking)
    intro_silence: float = 7.0      # Silence before voice (seconds)
    outro_silence: float = 4.5      # Silence after voice (seconds)
    ducking_enabled: bool = True    # Enable auto-ducking


class JingleService:
    """
    Service for creating jingles by mixing TTS with background music.
    Uses FFmpeg for audio processing with sidechaincompress for ducking.
    """

    def __init__(self):
        self.music_path = settings.MUSIC_PATH
        self.temp_path = settings.TEMP_PATH

    def _get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0

    def _find_music_file(self, music_filename: str) -> Optional[str]:
        """Find music file in storage"""
        # Try direct path first
        if os.path.isabs(music_filename) and os.path.exists(music_filename):
            return music_filename

        # Try in music directory
        music_path = os.path.join(self.music_path, music_filename)
        if os.path.exists(music_path):
            return music_path

        # Try with common extensions
        for ext in ['', '.mp3', '.wav', '.m4a']:
            test_path = os.path.join(self.music_path, f"{music_filename}{ext}")
            if os.path.exists(test_path):
                return test_path

        logger.error(f"Music file not found: {music_filename}")
        return None

    def _build_ducking_command(
        self,
        music_file: str,
        voice_file: str,
        output_file: str,
        config: JingleConfig,
        voice_duration: float,
        total_duration: float,
        fade_out_start: float
    ) -> list:
        """Build FFmpeg command with sidechaincompress ducking"""
        intro_ms = int(config.intro_silence * 1000)

        # Calculate threshold from duck_level
        # Higher duck_level = lower threshold = more ducking
        threshold = max(0.01, min(0.9, 1.0 - config.duck_level))

        # Sidechain compressor settings
        ratio = 6
        attack = 5
        release = 200
        makeup = 1.0

        # Build complex filter
        filter_complex = (
            f"[0:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.1f},"
            f"volume={config.music_volume:.2f}[music_loop];"
            f"[1:a]adelay={intro_ms}|{intro_ms},volume={config.voice_volume:.2f},"
            f"apad=whole_dur={total_duration:.1f}[voice_pad];"
            f"[voice_pad]asplit=2[vo][vd];"
            f"[music_loop][vd]sidechaincompress=threshold={threshold:.3f}:"
            f"ratio={ratio}:attack={attack}:release={release}:makeup={makeup:.1f}[music_ducked];"
            f"[music_ducked]afade=t=in:d={config.fade_in:.1f},"
            f"afade=t=out:st={fade_out_start:.1f}:d={config.fade_out:.1f}[music_final];"
            f"[music_final][vo]amix=inputs=2:duration=longest:dropout_transition=3[out]"
        )

        cmd = [
            'ffmpeg', '-y',
            '-i', music_file,
            '-i', voice_file,
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-t', f'{total_duration:.1f}',
            '-ac', '2',
            '-ar', '44100',
            '-codec:a', 'libmp3lame',
            '-b:a', '192k',
            output_file
        ]

        return cmd

    def _build_simple_mix_command(
        self,
        music_file: str,
        voice_file: str,
        output_file: str,
        config: JingleConfig,
        total_duration: float,
        fade_out_start: float
    ) -> list:
        """Build FFmpeg command for simple mix without ducking"""
        intro_ms = int(config.intro_silence * 1000)

        filter_complex = (
            f"[0:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.1f},"
            f"volume={config.music_volume:.2f},"
            f"afade=t=in:d={config.fade_in:.1f},"
            f"afade=t=out:st={fade_out_start:.1f}:d={config.fade_out:.1f}[music];"
            f"[1:a]adelay={intro_ms}|{intro_ms},volume={config.voice_volume:.2f},"
            f"apad=whole_dur={total_duration:.1f}[voice];"
            f"[music][voice]amix=inputs=2:duration=longest:dropout_transition=3[out]"
        )

        cmd = [
            'ffmpeg', '-y',
            '-i', music_file,
            '-i', voice_file,
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-t', f'{total_duration:.1f}',
            '-ac', '2',
            '-ar', '44100',
            '-codec:a', 'libmp3lame',
            '-b:a', '192k',
            output_file
        ]

        return cmd

    async def create_jingle(
        self,
        voice_audio_path: str,
        music_filename: str,
        output_path: str,
        config: Optional[JingleConfig] = None,
        voice_jingle_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a jingle by mixing voice audio with background music.

        Args:
            voice_audio_path: Path to the TTS audio file
            music_filename: Name of the music file (e.g., "Cool.mp3")
            output_path: Path for the output jingle file
            config: Optional JingleConfig, uses defaults if not provided
            voice_jingle_settings: Optional voice-specific jingle settings from DB

        Returns:
            Dict with success status, duration, and any error message
        """
        logger.info(f"Creating jingle with music: {music_filename}")

        # Use provided config or create default
        if config is None:
            config = JingleConfig()

        # Override with voice-specific settings if provided
        if voice_jingle_settings:
            if 'music_volume' in voice_jingle_settings:
                config.music_volume = voice_jingle_settings['music_volume']
            if 'voice_volume' in voice_jingle_settings:
                config.voice_volume = voice_jingle_settings['voice_volume']
            if 'duck_level' in voice_jingle_settings:
                config.duck_level = voice_jingle_settings['duck_level']
            if 'intro_silence' in voice_jingle_settings:
                config.intro_silence = voice_jingle_settings['intro_silence']
            if 'outro_silence' in voice_jingle_settings:
                config.outro_silence = voice_jingle_settings['outro_silence']

        try:
            # Find music file
            music_path = self._find_music_file(music_filename)
            if not music_path:
                return {
                    'success': False,
                    'error': f'Music file not found: {music_filename}'
                }

            # Get voice duration
            voice_duration = self._get_audio_duration(voice_audio_path)
            if voice_duration <= 0:
                return {
                    'success': False,
                    'error': 'Could not determine voice audio duration'
                }

            logger.info(f"Voice duration: {voice_duration:.2f}s")

            # Calculate timings
            voice_end_time = config.intro_silence + voice_duration
            total_duration = voice_end_time + config.outro_silence
            fade_out_start = max(voice_end_time, total_duration - config.fade_out)

            logger.info(
                f"Jingle timings: intro={config.intro_silence}s, "
                f"voice_end={voice_end_time:.2f}s, total={total_duration:.2f}s, "
                f"fade_out_start={fade_out_start:.2f}s"
            )

            # Build FFmpeg command
            if config.ducking_enabled:
                cmd = self._build_ducking_command(
                    music_path, voice_audio_path, output_path,
                    config, voice_duration, total_duration, fade_out_start
                )
            else:
                cmd = self._build_simple_mix_command(
                    music_path, voice_audio_path, output_path,
                    config, total_duration, fade_out_start
                )

            logger.info(f"Running FFmpeg command...")
            logger.debug(f"FFmpeg cmd: {' '.join(cmd)}")

            # Execute FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    'success': False,
                    'error': f'FFmpeg processing failed: {result.stderr[:500]}'
                }

            # Get output duration
            output_duration = self._get_audio_duration(output_path)

            logger.info(f"Jingle created successfully: {output_duration:.2f}s")

            return {
                'success': True,
                'duration': output_duration,
                'total_duration': total_duration,
                'music_file': music_filename
            }

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg process timed out")
            return {
                'success': False,
                'error': 'Audio processing timed out'
            }
        except Exception as e:
            logger.error(f"Error creating jingle: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


    async def add_announcement_sounds(
        self,
        voice_audio_path: str,
        output_path: str,
        intro_sound: str = "intro_announcement.mp3",
        outro_sound: str = "outro_announcement.mp3"
    ) -> Dict[str, Any]:
        """
        Add intro and outro announcement sounds to a voice audio file.

        Concatenates: intro_sound + voice_audio + outro_sound

        Uses FFmpeg filter_complex with concat filter to handle mixed formats
        (e.g., .m4a intro/outro with .mp3 voice).

        Args:
            voice_audio_path: Path to the TTS audio file
            output_path: Path for the output file
            intro_sound: Filename of intro sound in SOUNDS_PATH
            outro_sound: Filename of outro sound in SOUNDS_PATH

        Returns:
            Dict with success status, duration, and any error message
        """
        logger.info(f"Adding announcement sounds to: {voice_audio_path}")

        try:
            # Find sound files - must use absolute paths for FFmpeg
            intro_path = os.path.abspath(os.path.join(settings.SOUNDS_PATH, intro_sound))
            outro_path = os.path.abspath(os.path.join(settings.SOUNDS_PATH, outro_sound))
            voice_abs_path = os.path.abspath(voice_audio_path)
            output_abs_path = os.path.abspath(output_path)

            if not os.path.exists(intro_path):
                logger.warning(f"Intro sound not found: {intro_path}")
                return {
                    'success': False,
                    'error': f'Intro sound not found: {intro_sound}'
                }

            if not os.path.exists(outro_path):
                logger.warning(f"Outro sound not found: {outro_path}")
                return {
                    'success': False,
                    'error': f'Outro sound not found: {outro_sound}'
                }

            if not os.path.exists(voice_abs_path):
                logger.warning(f"Voice file not found: {voice_abs_path}")
                return {
                    'success': False,
                    'error': f'Voice file not found: {voice_audio_path}'
                }

            # Use filter_complex with concat filter - handles mixed formats automatically
            # This approach decodes all inputs and re-encodes, so format differences don't matter
            filter_complex = "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]"

            cmd = [
                'ffmpeg', '-y',
                '-i', intro_path,
                '-i', voice_abs_path,
                '-i', outro_path,
                '-filter_complex', filter_complex,
                '-map', '[out]',
                '-ac', '2',
                '-ar', '44100',
                '-codec:a', 'libmp3lame',
                '-b:a', '192k',
                output_abs_path
            ]

            logger.info(f"Running FFmpeg filter_complex concat...")
            logger.debug(f"FFmpeg cmd: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    'success': False,
                    'error': f'FFmpeg concat failed: {result.stderr[:500]}'
                }

            # Get output duration
            output_duration = self._get_audio_duration(output_abs_path)

            logger.info(f"Announcement audio created successfully: {output_duration:.2f}s")

            return {
                'success': True,
                'duration': output_duration,
                'intro_sound': intro_sound,
                'outro_sound': outro_sound
            }

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg process timed out")
            return {
                'success': False,
                'error': 'Audio processing timed out'
            }
        except Exception as e:
            logger.error(f"Error adding announcement sounds: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
jingle_service = JingleService()
