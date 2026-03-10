# Stack Recommendation: Python + LangGraph vs Node.js

## Recommendation: **Python + LangGraph + FastAPI**

For the Ghorahi Cement enterprise assistant backend, we recommend **Python with LangGraph and FastAPI**.

---

## Comparison

| Factor | Python + LangGraph | Node.js (TypeScript) |
|--------|--------------------|----------------------|
| **AI / agent orchestration** | **LangGraph is purpose-built**: explicit state graph (intent → tools → response), conditional edges, easy to add clarification steps or multi-tool flows. First-class tool-calling and guardrails. | Vercel AI SDK / LangChain.js exist but **no LangGraph equivalent**; you’d build a small custom orchestrator. Fine for a single linear flow, less so for evolving agent logic. |
| **LLM ecosystem** | **Richer**: LangChain, LangGraph, OpenAI SDK, structured output, Pydantic integration. Most examples and patterns are in Python. | Good (OpenAI SDK, LangChain.js) but fewer “agent graph” examples and less mature tool/orchestration patterns. |
| **Intent → tools → response** | **Natural fit**: LangGraph nodes = extract intent, execute tools, generate response. State flows along the graph; adding new tools or steps is a graph change. | You can do it with async/await and a simple pipeline; no standard graph model, so branching/multi-step gets ad-hoc. |
| **I/O (calling internal APIs)** | **Good**: `httpx` async client, FastAPI async endpoints. Enough for calling 1–3 internal APIs per request. | **Slightly better** for very high concurrency (many concurrent requests each doing I/O), but for leadership-scale traffic both are sufficient. |
| **Typing & validation** | **Strong**: Pydantic for request/response and LLM structured output. Type hints everywhere. | **Strong**: TypeScript + Zod or similar. Comparable. |
| **Deployment** | Same as any Python service: Docker, existing app server, or serverless (e.g. Lambda with adapter). | Same: Docker, Node server, or serverless. |
| **Team / existing site** | Your emp-portal is likely .NET; the assistant is a **separate service** either way. Python is a common choice for AI/ML backends. | If the rest of your stack were already Node/Next, one runtime could be convenient. Not a requirement here. |

---

## Why Python + LangGraph wins for this project

1. **Orchestration matches the design**  
   The design doc describes a clear flow: **intent/entity extraction → tool selection → tool execution → response generation (only from tool results)**. LangGraph models this as a **state graph**: each step is a node, and you can add branches (e.g. “need clarification”) or new tools without rewriting the pipeline.

2. **Tool-calling and anti-hallucination**  
   Tools (Sales Force API, future dispatch/production) are explicit nodes. The response node receives **only** tool outputs in state, so “answer only from API data” is enforced by graph structure, not only by prompt.

3. **Easier to extend**  
   When you add more APIs, more `Description_____` patterns, or comparison/summary flows, you extend the graph (new tool nodes or conditional edges). In Node you’d extend a custom pipeline by hand.

4. **Production-ready Python stack**  
   **FastAPI**: async, fast, automatic OpenAPI, easy to mount under your existing gateway.  
   **LangGraph**: production-oriented (checkpoints, streaming if needed later).  
   **httpx**: async HTTP client for calling emp-portal and other internal APIs.

5. **One language for the assistant backend**  
   All logic (intent, description filtering, tools, response generation) lives in Python. No context-switching between Node and a Python ML service.

---

## When Node.js might be preferable

- Your **entire** backend and frontend are already Node/TypeScript and you want a single runtime and one repo.
- The assistant flow will stay **very simple forever** (one LLM call + one API call + one response) with no multi-step or branching.
- Your team has no Python and no plan to support it.

Even then, a small Python + LangGraph service behind an API is straightforward to integrate from any frontend (including a .NET or Node site) via HTTP.

---

## Chosen stack (summary)

| Layer | Choice |
|-------|--------|
| **Language** | Python 3.11+ |
| **Orchestration** | LangGraph (state graph: intent → tools → response) |
| **HTTP API** | FastAPI (async, OpenAPI) |
| **LLM** | LangChain OpenAI (or Azure OpenAI); structured output for intent/entities |
| **Internal API client** | httpx (async) |
| **Config / env** | pydantic-settings, .env |
| **Description registry** | JSON config (description-registry); load at startup |

Frontend remains independent (your existing site + chat drawer); it calls `POST /api/assistant/chat` on this backend.
