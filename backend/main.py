from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from config import settings
from models import ChatRequest, ChatResponse, ConversationRequest, ConversationResponse
import ai_client

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Production-ready AI Chat API powered by Claude",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

_SKIP_AUTH = {"/", "/health"}


@app.on_event("startup")
async def startup_check():
    if not settings.api_key:
        raise RuntimeError("API_KEY environment variable is not set. Refusing to start.")


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path in _SKIP_AUTH:
        return await call_next(request)
    incoming = request.headers.get("X-API-Key", "")
    if not incoming or incoming != settings.api_key:
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


@app.get("/")
async def root():
    return {"status": "running", "version": settings.version}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "model": settings.model,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    result = await ai_client.chat(request.message, request.system_prompt, request.max_tokens)
    return ChatResponse(**result)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async def generate():
        async for text in ai_client.stream_chat(request.message, request.system_prompt, request.max_tokens):
            yield text

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/conversation", response_model=ConversationResponse)
async def conversation_endpoint(request: ConversationRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
    messages = [m.model_dump() for m in request.messages]
    result = await ai_client.conversation(messages, request.system_prompt, request.max_tokens)
    return ConversationResponse(**result)


@app.post("/conversation/stream")
async def conversation_stream(request: ConversationRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")
    messages = [m.model_dump() for m in request.messages]

    async def generate():
        async for text in ai_client.stream_conversation(messages, request.system_prompt, request.max_tokens):
            yield text

    return StreamingResponse(generate(), media_type="text/plain")
