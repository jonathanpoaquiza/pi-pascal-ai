from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Capacitacion AI Service"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = Field(default=120.0, gt=0)
    system_prompt: str = (
        "Eres un tutor educativo virtual experto en programación. "
        "Explica con claridad, usa ejemplos prácticos y adapta la respuesta "
        "al nivel del estudiante. Responde siempre en español."
    )
    cors_origins: list[str] = ["http://localhost:3000"]
    max_messages: int = Field(default=40, ge=1, le=100)
    max_message_characters: int = Field(default=12000, ge=100, le=50000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AI_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()