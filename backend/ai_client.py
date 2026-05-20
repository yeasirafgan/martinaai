from anthropic import AsyncAnthropic
from config import settings

client = AsyncAnthropic(api_key=settings.claude_api_key)


async def chat(message: str, system_prompt: str, max_tokens: int) -> dict:
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


async def stream_chat(message: str, system_prompt: str, max_tokens: int):
    async with client.messages.stream(
        model=settings.model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": message}]
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def conversation(messages: list, system_prompt: str, max_tokens: int) -> dict:
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


async def stream_conversation(messages: list, system_prompt: str, max_tokens: int):
    async with client.messages.stream(
        model=settings.model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages
    ) as stream:
        async for text in stream.text_stream:
            yield text
