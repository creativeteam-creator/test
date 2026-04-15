from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    storage_dir: Path = Field(default=Path("storage"), alias="STORAGE_DIR")
    cors_allow_origins: List[str] = Field(default=["*"], alias="CORS_ALLOW_ORIGINS")

    sd_base_url: str = Field(default="http://127.0.0.1:7860", alias="SD_BASE_URL")
    sd_timeout_seconds: int = Field(default=120, alias="SD_TIMEOUT_SECONDS")

    google_tts_credentials_json: str = Field(default="", alias="GOOGLE_TTS_CREDENTIALS_JSON")
    default_voice_name: str = Field(default="en-US-Neural2-C", alias="DEFAULT_VOICE_NAME")
    default_voice_language_code: str = Field(default="en-US", alias="DEFAULT_VOICE_LANGUAGE_CODE")

    ffmpeg_path: str = Field(default="ffmpeg", alias="FFMPEG_PATH")
    ffprobe_path: str = Field(default="ffprobe", alias="FFPROBE_PATH")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
