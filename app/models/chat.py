from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

Role = Literal["user", "assistant", "system"]


class Message(BaseModel):
    role: Role
    content: Annotated[str, Field(min_length=1, max_length=50000)]

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message content cannot be blank")
        return cleaned


class ChatRequest(BaseModel):
    messages: Annotated[list[Message], Field(min_length=1, max_length=100)]
