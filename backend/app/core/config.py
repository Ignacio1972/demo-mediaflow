from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # General
    APP_NAME: str = "MediaFlowDemo"
    APP_VERSION: str = "2.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # ElevenLabs
    ELEVENLABS_API_KEY: str
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    ELEVENLABS_BASE_URL: str = "https://api.elevenlabs.io/v1"

    # Anthropic Claude
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS: int = 500

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_RECONNECT_INTERVAL: int = 3

    # Storage
    STORAGE_PATH: str = "/app/storage"
    AUDIO_PATH: str = "/app/storage/audio"
    MUSIC_PATH: str = "/app/storage/music"
    SOUNDS_PATH: str = "/app/storage/sounds"
    TEMP_PATH: str = "/app/storage/temp"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        return json.loads(self.CORS_ORIGINS)

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Audio Processing
    DEFAULT_TARGET_LUFS: float = -16.0
    DEFAULT_SAMPLE_RATE: int = 44100
    DEFAULT_BITRATE: str = "192k"

    # Player Integration
    PLAYER_POLLING_INTERVAL: int = 2
    PLAYER_WEBSOCKET_URL: str = "ws://localhost:8000/ws/player"

    # AzuraCast Integration
    AZURACAST_URL: str = "http://localhost:10080"
    AZURACAST_API_KEY: str = ""
    AZURACAST_STATION_ID: int = 1
    AZURACAST_STATION_NAME: str = "mediaflow"
    AZURACAST_MEDIA_FOLDER: str = "Grabaciones"

    # Tenant Configuration (Multi-tenant support)
    TENANT_ID: str = "demo"
    TENANT_NAME: str = "MediaFlow Demo"
    TENANT_LOGO: str = "/images/mediaflow-logo.png"
    TENANT_PRIMARY_COLOR: str = "#4F46E5"
    TENANT_SECONDARY_COLOR: str = "#7C3AED"
    TENANT_DOMAIN: str = "localhost"
    TENANT_FAVICON: str = "/favicon.ico"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
