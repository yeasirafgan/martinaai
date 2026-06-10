import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

AUTH = {"X-API-Key": "dummy_api_key_for_tests"}


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
    response = client.post("/chat", json={"message": "  "}, headers=AUTH)
    assert response.status_code == 400


def test_conversation_empty_messages():
    response = client.post("/conversation", json={"messages": []}, headers=AUTH)
    assert response.status_code == 400


def test_missing_api_key_returns_401():
    response = client.post("/chat", json={"message": "Hi"})
    assert response.status_code == 401


def test_wrong_api_key_returns_401():
    response = client.post("/chat", json={"message": "Hi"}, headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


@patch("ai_client.client")
def test_chat_success(mock_client):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello!")]
    mock_response.model = "claude-sonnet-4-6"
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 5
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    response = client.post("/chat", json={"message": "Hi"}, headers=AUTH)
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
    response = client.post("/conversation", json={"messages": messages}, headers=AUTH)
    assert response.status_code == 200
    assert response.json()["reply"] == "I remember you."
