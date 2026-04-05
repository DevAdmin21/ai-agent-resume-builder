from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Dict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4.1-nano-2025-04-14"
    openai_temperature: float = 0.2
    openai_max_tokens: int = 2048

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    output_dir: str = "outputs"

    # Validation
    max_text_length: int = 50_000
    min_text_length: int = 50


@lru_cache()
def get_settings() -> Settings:
    return Settings()