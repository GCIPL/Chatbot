# Ghorahi Assistant Backend (Python + LangGraph + FastAPI)

Stack: **Python 3.11+** (3.11 or 3.12 recommended), **LangGraph**, **FastAPI**, **LangChain OpenAI**. Answers only from **description + quantity** (no value).

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set OPENAI_API_KEY (or Azure OpenAI vars) and optionally EMP_PORTAL_*.
```

## Run

```bash
# From backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/health`
- Chat: `POST http://localhost:8000/api/assistant/chat` with body `{"message": "Today sales kati cha?"}`

## Flow (LangGraph)

1. **extract_intent** — LLM extracts time_scope, product, intent from question.
2. **run_tools** — Calls emp-portal Sales Force `returnData?ABC=108` (ChatBot metrics), normalizes each row into `description`, `metric_type`, and `quantity`, then filters rows by question (description registry and metric type).
3. **generate_response** — LLM generates reply from **only** the filtered rows (description + quantity + type); no value/amount.

## Config

- **.env** — `OPENAI_API_KEY`, `EMP_PORTAL_BASE_URL`, `SALES_FORCE_ABC`. Optional: `OPENAI_API_BASE` for Azure.
- **Description registry** — Repo root `config/description-registry.example.json` maps question hints to description substrings for filtering. Extend as you add APIs/labels.

## Project layout

```
backend/
  app/
    api/          # FastAPI routes (assistant chat)
    internal_api/ # Emp-portal HTTP client (description + quantity only)
    service/     # Intent, tools, description filter, response generator, graph
    prompts.py
    config.py
    models.py
    main.py
  requirements.txt
  .env.example
```

## Session (auth)

To pass the user's session cookie to the emp-portal, the frontend can send it in a header (e.g. `X-Session-Cookie`). In `api/assistant.py`, set `initial["session_cookie"]` from that header. Do not log or expose the cookie.
