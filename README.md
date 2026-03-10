# Ghorahi Cement — Enterprise AI Assistant

This repository holds the **production design and integration assets** for the Ghorahi Cement Leadership Assistant: an embedded, right-side chat drawer inside the existing internal website.

## Purpose

- **Not a standalone app.** The assistant is designed to be integrated into the existing Ghorahi Cement website (header or FAB trigger → right-side drawer).
- **Controlled and audited.** Answers are based only on internal APIs (Sales Order, Sales Dispatch, Production). No hallucinated business data.
- **Leadership-focused.** Supports English and Nepali/mixed queries, voice input, and text-to-speech for replies.

## Docs

| Document | Description |
|----------|-------------|
| [docs/PRODUCTION_ASSISTANT_DESIGN.md](docs/PRODUCTION_ASSISTANT_DESIGN.md) | Full 30-section product and technical design (architecture, UX, security, phases, risks, folder structure). |
| [docs/assistant-api.md](docs/assistant-api.md) | API contract for the chat endpoint used by the frontend. |
| [docs/internal-api-catalog.md](docs/internal-api-catalog.md) | Internal portal APIs; **question → check description → answer only from those rows**. Extensible as you add more descriptions. |
| [config/description-registry.example.json](config/description-registry.example.json) | Question hints → description patterns; extend as you add APIs/labels. |
| [config/featureFlags.example.json](config/featureFlags.example.json) | Example feature flags (drawer, voice, TTS, roles). |

## Design highlights

- **UI:** Right-side chat drawer; trigger in existing header or FAB; native look and feel.
- **Backend:** Single assistant API that performs intent extraction → tool calls to your APIs → response generation from results only.
- **Voice:** Browser STT for input; TTS for last assistant reply (concise version).
- **Safety:** Response generator receives only tool results; anti-hallucination guardrails and clear “no data” messaging.
- **Ops:** Audit logging, RBAC via existing auth, feature flags, phased rollout.

## Backend (Python + LangGraph + FastAPI)

The assistant backend is implemented in **Python** with **LangGraph** and **FastAPI**. See [docs/STACK_RECOMMENDATION.md](docs/STACK_RECOMMENDATION.md) for why this stack was chosen over Node.js.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY and optionally EMP_PORTAL_*
uvicorn app.main:app --reload --port 8000
```

- **Health:** `GET http://localhost:8000/health`
- **Chat:** `POST http://localhost:8000/api/assistant/chat` with `{"message": "Today sales kati cha?"}`

Flow: **intent extraction → run tools (emp-portal Sales Force) → filter by description → generate response** (description + quantity only; no value). See [backend/README.md](backend/README.md).

## Demo

- **Guide:** [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) — how to run and present the assistant.
- **Browser demo:** Open `demo/chat-demo.html` in Chrome/Edge after starting the backend; type a question and click Send.

## Next steps

1. Set `OPENAI_API_KEY` in `backend/.env` for LLM-powered intent and response.
2. Add the chat drawer to your existing website; call `POST /api/assistant/chat`.
3. Optionally forward session cookie (e.g. `X-Session-Cookie`) for emp-portal auth.
4. Roll out behind a feature flag; pilot with a few users before full leadership rollout.
