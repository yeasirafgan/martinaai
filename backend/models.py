from pydantic import BaseModel, field_validator
from typing import Optional


class Message(BaseModel):
    role: str
    content: str



class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = "You are a helpful AI assistant."
    max_tokens: Optional[int] = 1024



class ChatResponse(BaseModel):
    reply: str
    model: str
    input_tokens: int
    output_tokens: int



class ConversationRequest(BaseModel):
    messages: list[Message]
    system_prompt: Optional[str] = "You are a helpful AI assistant."
    max_tokens: Optional[int] = 1024

    @field_validator("messages")
    @classmethod
    def max_messages(cls, v: list) -> list:
        if len(v) > 100:
            raise ValueError("Maximum 100 messages per request")
        return v

    @field_validator("max_tokens")
    @classmethod
    def cap_max_tokens(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v > 4096:
            return 4096
        return v



class ConversationResponse(BaseModel):
    reply: str
    model: str
    total_messages: int
