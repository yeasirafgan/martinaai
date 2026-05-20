import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data
    assert "version" in data


def test_chat_empty_message():
    response = client.post("/chat", json={"message": "  "})
    assert response.status_code == 400


def test_conversation_empty_messages():
    response = client.post("/conversation", json={"messages": []})
    assert response.status_code == 400


@patch("ai_client.client")
def test_chat_success(mock_client):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello!")]
    mock_response.model = "claude-sonnet-4-6"
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 5
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    response = client.post("/chat", json={"message": "Hi"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Hello!"


@patch("ai_client.client")
def test_conversation_success(mock_client):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="I remember you.")]
    mock_response.model = "claude-sonnet-4-6"
    mock_response.usage.input_tokens = 20
    mock_response.usage.output_tokens = 8
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    messages = [
        {"role": "user", "content": "My name is Yeasir"},
        {"role": "assistant", "content": "Nice to meet you, Yeasir."},
        {"role": "user", "content": "What is my name?"},
    ]
    response = client.post("/conversation", json={"messages": messages})
    assert response.status_code == 200
    assert response.json()["reply"] == "I remember you."
