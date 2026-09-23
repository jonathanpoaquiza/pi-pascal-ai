from collections.abc import AsyncIterator
import json
from typing import Any

import httpx

from app.core.config import Settings
from app.models.chat import Message


class LLMServiceError(RuntimeError):
    """Raised when the configured LLM cannot generate a response."""


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def stream_chat(self, messages: list[Message]) -> AsyncIterator[str]:
        payload = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": self.settings.system_prompt},
                *[message.model_dump() for message in messages],
            ],
            "stream": True,
        }
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"

        try:
            timeout = httpx.Timeout(self.settings.ollama_timeout_seconds, read=None)
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code >= 400:
                        detail = (await response.aread()).decode("utf-8", errors="replace")
                        raise LLMServiceError(
                            f"Ollama respondió {response.status_code}: {detail[:500]}"
                        )
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data: dict[str, Any] = json.loads(line)
                        except json.JSONDecodeError as error:
                            raise LLMServiceError("Ollama devolvió un fragmento inválido") from error
                        if data.get("error"):
                            raise LLMServiceError(str(data["error"]))
                        token = data.get("message", {}).get("content", "")
                        if token:
                            yield token
        except LLMServiceError:
            raise
        except (httpx.HTTPError, OSError) as error:
            raise LLMServiceError(
                "No se pudo conectar con Ollama. Verifica que esté ejecutándose "
                "y que el modelo configurado exista."
            ) from error