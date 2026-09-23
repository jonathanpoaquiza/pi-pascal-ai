from collections.abc import AsyncIterator
import json
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.config import get_settings
from app.models.chat import ChatRequest
from app.services.llm_service import LLMService, LLMServiceError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
llm_service = LLMService(settings)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Streaming AI tutor service backed by Ollama.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


def _sse_event(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=True)}\n\n"


async def _stream_chat(request: ChatRequest, http_request: Request) -> AsyncIterator[str]:
    try:
        async for token in llm_service.stream_chat(request.messages):
            if await http_request.is_disconnected():
                return
            yield _sse_event("token", {"content": token})
        yield _sse_event("done", {"finish_reason": "stop"})
    except LLMServiceError as error:
        logger.exception("LLM provider request failed")
        yield _sse_event("error", {"message": str(error)})


@app.post("/api/chat", tags=["chat"])
async def chat(request: ChatRequest, http_request: Request) -> StreamingResponse:
    return StreamingResponse(
        _stream_chat(request, http_request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.exception_handler(LLMServiceError)
async def llm_error_handler(_: Request, error: LLMServiceError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(error)})