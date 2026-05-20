# Martinaai

[![CI](https://github.com/yeasirafgan/martinaai/actions/workflows/ci.yml/badge.svg)](https://github.com/yeasirafgan/martinaai/actions/workflows/ci.yml)

**Live demo:** [martinaai.vercel.app](https://martinaai.vercel.app)

A production-ready AI chat application built with **FastAPI**, **Claude API**, and **Next.js**. Features real-time streaming responses, multi-turn conversation memory, and a clean ChatGPT-style interface.

---

## Screenshots

![Stream mode — multi-turn conversation](docs/screenshot-stream.png)
*Stream mode: tokens appear in real time as Claude generates them*

![Instant mode — formatted response](docs/screenshot-instant.png)
*Instant mode: full response delivered at once with loading indicator*

---

## Features

- **Streaming responses** — tokens stream to the UI in real time via `StreamingResponse`
- **Instant mode** — full response with animated loading indicator
- **Conversation memory** — full message history sent on every request so Claude remembers context
- **Multi-chat sidebar** — create, switch between, and delete conversations
- **Error handling** — rate limits, API errors, and connection failures return proper HTTP responses
- **REST API** — clean endpoints for both single-turn and multi-turn use cases
- **Interactive API docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- **Dockerised** — single `docker compose up` runs the full stack

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI | Anthropic Claude API (`claude-sonnet-4-6`) |
| Validation | Pydantic v2, pydantic-settings |
| Frontend | Next.js 14, React 18, Tailwind CSS |
| Testing | pytest, httpx |
| CI | GitHub Actions |
| Containerisation | Docker, Docker Compose |
| Deploy | Railway (backend), Vercel (frontend) |

---

## Architecture

```
Browser
  │
  ▼
Next.js (port 4000)
  │  fetch POST /conversation/stream
  ▼
FastAPI (port 3000)
  │  AsyncAnthropic.messages.stream()
  ▼
Claude API
  │  text chunks
  ▼
FastAPI StreamingResponse  ──►  Next.js ReadableStream  ──►  UI renders token by token
```

Each user message is sent with the full conversation history so Claude maintains context across turns. For non-streaming mode, `/conversation` returns the complete response in one JSON payload.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Status check |
| `GET` | `/health` | Version, model, app info |
| `POST` | `/chat` | Single message → full response |
| `POST` | `/chat/stream` | Single message → streaming response |
| `POST` | `/conversation` | Message history → full response |
| `POST` | `/conversation/stream` | Message history → streaming response |

### Example — streaming conversation

```bash
curl -X POST http://localhost:3000/conversation/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is a RAG pipeline?"}
    ],
    "max_tokens": 1024
  }'
```

### Example — health check

```bash
curl http://localhost:3000/health
# {"status":"healthy","app":"Martinaai","version":"1.0.0","model":"claude-sonnet-4-6"}
```

---

## Run Locally

### Prerequisites

- Docker Desktop running
- Claude API key from [console.anthropic.com](https://console.anthropic.com)

### Backend

```bash
cd backend
cp .env.example .env
# Add your CLAUDE_API_KEY to .env
docker compose up --build
```

API runs at `http://localhost:3000` — Swagger UI at `http://localhost:3000/docs`

### Frontend

```bash
cd frontend
docker compose up --build
```

UI runs at `http://localhost:4000`

---

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## Project Structure

```
martinaai/
├── .github/workflows/ci.yml  # GitHub Actions — lint + test on every push
├── backend/
│   ├── config.py             # Settings loaded from .env via pydantic-settings
│   ├── models.py             # Pydantic request/response schemas
│   ├── ai_client.py          # Claude API — streaming + regular, error handling
│   ├── main.py               # FastAPI app, CORS, all routes
│   ├── tests/
│   │   └── test_endpoints.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── frontend/
    ├── src/components/
    │   ├── Chat.tsx          # State, API calls, conversation management
    │   ├── MessageBubble.tsx
    │   └── InputBar.tsx
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Environment Variables

```env
CLAUDE_API_KEY=your_api_key_here
MODEL=claude-sonnet-4-6
ALLOWED_ORIGINS=http://localhost:4000
```

---

## Deploy

### Backend → Railway

1. Connect GitHub repo to Railway
2. Set root directory to `backend`
3. Add environment variables: `CLAUDE_API_KEY`, `MODEL`, `ALLOWED_ORIGINS`
4. Railway auto-detects the Dockerfile and deploys

### Frontend → Vercel

1. Connect GitHub repo to Vercel
2. Set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app`
4. Deploy

---

## Author

**Yeasir Afgan** — [GitHub](https://github.com/yeasirafgan)

---

## Licence

[MIT](LICENSE)
