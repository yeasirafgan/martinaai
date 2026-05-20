from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    role: str        # "user" or "assistant"
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


class ConversationResponse(BaseModel):
    reply: str
    model: str
    total_messages: int
