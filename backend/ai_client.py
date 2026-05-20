from anthropic import AsyncAnthropic, APIStatusError, APIConnectionError, RateLimitError
from fastapi import HTTPException
from config import settings

client = AsyncAnthropic(api_key=settings.claude_api_key)


def _handle_anthropic_error(e: Exception) -> None:
    if isinstance(e, RateLimitError):
        raise HTTPException(status_code=429, detail="Rate limit reached. Please try again shortly.")
    if isinstance(e, APIStatusError):
        raise HTTPException(status_code=e.status_code, detail=f"Claude API error: {e.message}")
    if isinstance(e, APIConnectionError):
        raise HTTPException(status_code=503, detail="Could not reach Claude API. Check your connection.")
    raise HTTPException(status_code=500, detail="Unexpected error calling Claude API.")


async def chat(message: str, system_prompt: str, max_tokens: int) -> dict:
    try:
        response = await client.messages.create(
            model=settings.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        )
        return {
            "reply": response.content[0].text,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    except (RateLimitError, APIStatusError, APIConnectionError) as e:
        _handle_anthropic_error(e)


async def stream_chat(message: str, system_prompt: str, max_tokens: int):
    try:
        async with client.messages.stream(
            model=settings.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": message}]
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except (RateLimitError, APIStatusError, APIConnectionError) as e:
        _handle_anthropic_error(e)


async def conversation(messages: list, system_prompt: str, max_tokens: int) -> dict:
    try:
        response = await client.messages.create(
            model=settings.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        )
        return {
            "reply": response.content[0].text,
            "model": response.model,
            "total_messages": len(messages) + 1,
        }
    except (RateLimitError, APIStatusError, APIConnectionError) as e:
        _handle_anthropic_error(e)


async def stream_conversation(messages: list, system_prompt: str, max_tokens: int):
    try:
        async with client.messages.stream(
            model=settings.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except (RateLimitError, APIStatusError, APIConnectionError) as e:
        _handle_anthropic_error(e)
