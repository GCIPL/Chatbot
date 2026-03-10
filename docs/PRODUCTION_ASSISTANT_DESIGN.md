# Ghorahi Cement Enterprise AI Assistant — Production Design

**Document type:** Product & technical design for embedded leadership assistant  
**Scope:** Right-side chat drawer integrated into existing Ghorahi Cement internal website  
**Status:** Production-oriented, phase-wise delivery

---

## 1. Product Summary

**Name:** Ghorahi Cement Leadership Assistant (embedded)

**What it is:** A production-grade, embedded AI assistant that lives inside the existing Ghorahi Cement internal website. Leadership opens a right-side chat drawer, asks business questions in English or Nepali (typed or voice), and receives answers grounded only in internal APIs (Sales Order, Sales Dispatch, Production). Responses are shown on-screen and can be read aloud via text-to-speech. The assistant never invents data; it answers only from API results and clearly states when data is missing or ambiguous.

**What it is not:** A generic chatbot, a separate app, or a demo. It is a controlled, audited, role-aware feature of the current website.

**Value:** Faster access to sales, dispatch, and production insights for leadership without leaving the existing system or learning new tools.

---

## 2. Business Objectives

| Objective | Description |
|-----------|-------------|
| **Speed** | Reduce time to answer “today’s dispatch”, “this month’s clinker sales”, “plant-wise production” from minutes to seconds. |
| **Single surface** | Keep all workflows inside the existing website; no new URLs or apps for leadership. |
| **Trust** | Answers sourced only from internal APIs; no hallucinated numbers. |
| **Accessibility** | Support voice input and TTS for hands-free or low-vision use. |
| **Auditability** | Full audit trail of questions, API calls, and responses for compliance and improvement. |
| **Scale** | Design for concurrent leadership usage and future expansion (more products, plants, regions). |

---

## 3. User Roles and Access Model

| Role | Access | Notes |
|------|--------|------|
| **Leadership** | Full assistant: all query types, voice, TTS, all products/plants. | Primary persona. |
| **Department heads / Managers** | Same or subset of query types; scope may be restricted by plant/region if enforced by backend. | Reuse same RBAC as rest of site. |
| **Viewer / Read-only** | Optional: allow only predefined summaries or restrict to certain metrics. | Configurable via feature flags. |
| **Unauthenticated** | No access to assistant; drawer trigger hidden or disabled. | Reuse existing website auth. |

**Access model:** Reuse existing website authentication and session. Assistant checks session and, if the backend supports it, role/permissions from the same identity store. No separate login for the assistant.

---

## 4. Detailed Use Cases

| ID | Use case | Actor | Flow | Success |
|----|----------|-------|------|---------|
| UC-1 | Typed business question | Leadership | Open drawer → type “Today sales order kati cha?” → see answer with numbers and source hint | Answer reflects API data only; user can expand or hear TTS |
| UC-2 | Voice question | Leadership | Open drawer → tap mic → speak “OPC production today” → see transcribed text and answer | Correct transcription and same quality answer as typed |
| UC-3 | Listen to answer | Leadership | After answer → tap “Read aloud” → hear concise TTS | TTS is concise and matches on-screen summary |
| UC-4 | Summary request | Leadership | “Give me today summary” → see sales order, dispatch, production summary | Single structured summary from multiple APIs |
| UC-5 | Comparison | Leadership | “Compare today vs yesterday production” → see comparison table or narrative | Both time ranges from API; no invented data |
| UC-6 | Product/plant/region drill-down | Leadership | “Yesterday plant-wise dispatch” or “This month clinker sales order” | Filtered by product/plant/region as supported by APIs |
| UC-7 | Missing or ambiguous data | Leadership | Ask for a metric or period with no data → clear message: “No data for X” or “Please specify Y” | No hallucination; safe, clear messaging |
| UC-8 | Unsupported question | Leadership | Ask off-topic or unsupported question → polite boundary message and suggestion of supported types | User understands scope of assistant |

---

## 5. Full Feature Scope

**In scope (Phase 1–2):**

- Right-side chat drawer in existing website (trigger: header button or FAB).
- Text input and send; conversation history in session (optional persistence in Phase 2).
- Voice input: browser Speech-to-Text → same pipeline as text.
- Intent/entity extraction (query type, filters: product, plant, region, date range).
- Tool-calling to internal APIs: Sales Order, Sales Dispatch, Production (and any existing summary/comparison APIs).
- Response generation from API results only; structured + short narrative; no fabrication.
- Text-to-speech for last assistant reply (concise version).
- Role-based access: drawer visibility and backend enforcement using existing auth.
- Audit logging: user, question, intent, tools called, response summary, timestamp.

**In scope (later phases):**

- Cross-metric comparisons, trend answers, top/bottom performance (as APIs support).
- Optional persisted conversation history per user.
- Export or share answer (e.g. copy link, PDF).

**Out of scope:**

- Generic chitchat or non–business-domain answers (bounded with a clear boundary message).
- Creating or modifying orders/dispatch/production (read-only assistant).
- Replacing existing reports; assistant complements them.

---

## 6. Right-Side Chat Drawer UX Design

- **Placement:** Right side of viewport; overlay or push (configurable). Width: e.g. 400–480px on desktop; full-width or near full-width on small screens.
- **Trigger:** Persistent control in existing website header **or** floating action button (FAB) bottom-right. Single source of truth (e.g. one config flag: `ASSISTANT_TRIGGER=header|fab`).
- **Opening:** Click trigger → drawer slides in from right; focus moves to drawer; first focusable element (input or “New chat”) focused for accessibility.
- **Content:**  
  - **Header:** “Assistant” or “Ghorahi Assistant”, optional “New chat”, close (X).  
  - **Body:** Message list (user + assistant bubbles). Assistant messages: optional “Read aloud” control.  
  - **Footer:** Text input, send button, microphone button (hold-to-talk or tap-to-toggle per design).
- **Feel:** Reuse existing site typography, colors, and spacing so the drawer feels like a native feature. No distinct “product” branding that makes it feel like a third-party widget.
- **Empty state:** Short hint: “Ask about sales orders, dispatch, or production” and 2–3 example prompts.
- **Loading:** Inline loading indicator for “Assistant is thinking” and optional “Checking sales data…” for tool calls.
- **Errors:** Inline error message with retry; no full-page error inside drawer.

---

## 7. Voice Interaction Design

- **Input:** Browser Web Speech API (SpeechRecognition) or enterprise-approved alternative. Language: Nepali and/or English (configurable). UX: tap mic → speak → auto-stop or manual stop → transcript sent as user message.
- **Output:** Text-to-speech for the **last** assistant message only. Use a concise “speech” version of the reply (e.g. one short paragraph) even if on-screen content is longer or structured. Prefer same language as query when feasible (e.g. Nepali query → Nepali TTS if supported).
- **Feedback:** Mic button state (idle / listening / processing). Optional live transcript preview before send.
- **Fallback:** If STT fails or is unsupported, show message and keep text input as primary path.

---

## 8. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Drawer opens from header or FAB; closes with X or outside click. | P0 |
| FR-2 | User can send a text message and receive one assistant reply per turn. | P0 |
| FR-3 | User can start voice input; system converts speech to text and sends as message. | P0 |
| FR-4 | System infers intent (e.g. sales order, dispatch, production, summary, comparison) and entities (product, plant, region, date range). | P0 |
| FR-5 | System calls only allowed internal APIs with derived parameters; no arbitrary external APIs. | P0 |
| FR-6 | Assistant response is generated only from API responses; no invented numbers or facts. | P0 |
| FR-7 | User can trigger TTS for the last assistant message. | P1 |
| FR-8 | If data is missing or ambiguous, response states that clearly and suggests clarification. | P0 |
| FR-9 | Unsupported or off-topic questions receive a polite boundary message and list of supported query types. | P0 |
| FR-10 | All questions, intents, API calls, and response summaries are logged for audit. | P0 |
| FR-11 | Access to assistant and to specific query types is enforced by role (reuse site RBAC). | P0 |
| FR-12 | Session or persisted conversation history (configurable). | P1 |

---

## 9. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | **Latency** | P95 reply time &lt; 10 s for single-API questions; &lt; 15 s for multi-API/summary. |
| NFR-2 | **Availability** | Assistant endpoint aligned with existing website SLA (e.g. 99.5%+). |
| NFR-3 | **Security** | No PII in logs beyond user ID; credentials and API keys only on backend. |
| NFR-4 | **Scalability** | Support concurrent leadership users; stateless backend; optional queue for AI. |
| NFR-5 | **Maintainability** | Modular frontend and backend; clear separation between orchestration, tools, and UI. |
| NFR-6 | **Observability** | Logs, metrics (request count, latency, error rate), and optional tracing. |

---

## 10. System Architecture Integrated into Existing Website

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EXISTING GHORAHI CEMENT WEBSITE                          │
│  ┌──────────────────────────────────────────────────┐  ┌──────────────────┐  │
│  │  Header / FAB (existing + assistant trigger)      │  │  Right-side      │  │
│  │  Auth / session (existing)                        │  │  Chat Drawer     │  │
│  └──────────────────────────────────────────────────┘  │  (new component) │  │
│                                                         └────────┬─────────┘  │
└─────────────────────────────────────────────────────────────────┼────────────┘
                                                                  │
                                    HTTPS (same origin / API base) │
                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EXISTING OR NEW BACKEND API LAYER                        │
│  ┌─────────────────┐  ┌─────────────────────────────────────────────────┐   │
│  │  Auth middleware │  │  Assistant API (e.g. /api/assistant/chat)         │   │
│  │  (reuse existing)│  │  - Validate session, RBAC                        │   │
│  └────────┬────────┘  │  - Audit log write                                │   │
│           │           │  - Call Assistant Service                         │   │
│           ▼           └────────────────────────┬──────────────────────────┘   │
│  ┌─────────────────┐                            │                            │
│  │  Existing APIs   │  Sales Order / Dispatch / Production (your APIs)      │
│  └─────────────────┘                            │                            │
└──────────────────────────────────────────────────┼──────────────────────────┘
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ASSISTANT SERVICE (new or extended)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Intent +     │  │ Tool         │  │ Internal     │  │ Response         │  │
│  │ Entity       │  │ Executor     │  │ API Client   │  │ Generator       │  │
│  │ Extraction   │  │              │  │ (Sales,      │  │ (from results    │  │
│  │              │  │              │  │  Dispatch,   │  │  only)          │  │
│  │              │  │              │  │  Production) │  │                  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                 │                    │            │
│         └─────────────────┴─────────────────┴────────────────────┘            │
│                                   │                                          │
│                         ┌─────────▼─────────┐                                 │
│                         │  AI Orchestrator  │  (LLM for intent + response)   │
│                         └──────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Integration points:**

- **Frontend:** One new route or layout area that renders the drawer; trigger in existing header or FAB; reuse existing auth/session (e.g. cookie or token sent with every request).
- **Backend:** One assistant route (e.g. `POST /api/assistant/chat`) that validates session, checks role, logs audit, calls Assistant Service, returns reply (+ optional speech snippet for TTS).
- **Existing APIs:** Assistant Service calls your existing Sales Order, Sales Dispatch, and Production APIs as internal HTTP or server-side calls; no direct exposure to the client.

---

## 11. Frontend Component Architecture

Assumed stack: React (or Vue) inside existing app. Naming is framework-agnostic.

- **AssistantProvider (or context):** Provides session identity, API base URL, feature flags (e.g. voice on/off, TTS on/off), and open/close state. Wraps the part of the app where the drawer is available.
- **AssistantTrigger:** Renders header button or FAB; opens drawer; respects feature flag and RBAC (hide if no access).
- **AssistantDrawer:** Container for the right-side panel; handles open/close animation, focus trap, and responsive width.
- **AssistantHeader:** Title, “New chat”, close button.
- **Conversation:** Scrollable list of messages (user + assistant). Each message: role, content, timestamp, optional “Read aloud” for assistant.
- **MessageBubble (User | Assistant):** Renders one message; assistant bubble includes TTS button and optional “Source: Sales API” hint.
- **InputArea:** Text field + send + mic button. Disabled while loading.
- **VoiceInput:** Wraps mic button; uses Web Speech API; emits transcript as message text.
- **TTSPlayer:** Plays concise version of last assistant message; stop on new message or user request.

**State:** Conversation messages in component state or global store (e.g. React state or Zustand). Optional: persist to backend in Phase 2.

**API:** Single `postMessage(userMessage)` → returns `{ reply, replyForTts?, error? }`. Frontend never calls internal business APIs directly.

---

## 12. Backend Service Architecture

- **Assistant API (HTTP):** Thin layer: auth, RBAC, audit log write, parse body, call Assistant Service, return JSON.
- **Assistant Service (application layer):** Orchestrates the flow: intent/entity extraction → tool selection → tool execution (internal API client) → response generation. No direct DB access for business data; all from APIs.
- **Intent/Entity Service:** Uses LLM or rule-based parser to return structured intent + entities (query type, product, plant, region, date range).
- **Tool Registry:** Maps intents to tools (e.g. “sales_order” → SalesOrderTool). Each tool knows which internal API to call and how to map entities to query params.
- **Internal API Client:** HTTP client to your existing Sales Order, Dispatch, Production (and summary/comparison) APIs; handles timeouts, retries, and error mapping.
- **Response Generator:** Takes tool results only; produces narrative + structured snippet; never injects data that was not in the results. Optional: separate “speech” version for TTS.

**Patterns:** Strategy for tools, Factory for creating tool instances, Dependency Injection for API client and LLM client so they can be mocked and tested.

---

## 13. AI Orchestration and Tool-Calling Design

- **Orchestrator:** Single LLM call for intent/entity extraction; then deterministic tool dispatch based on intent; then second LLM call (or template) for response generation with **only** tool results in context.
- **Tool-calling flow:**  
  1. User message → Intent/Entity extraction (LLM or hybrid).  
  2. Map intent to one or more tools (e.g. “today summary” → [SalesOrderTool, DispatchTool, ProductionTool]).  
  3. Execute tools with entity-derived params (date, product, plant, etc.).  
  4. Collect all results; if any tool fails, include error in context.  
  5. Response generation: system prompt + user message + **only** tool results (no extra knowledge). Generate text and optional short TTS version.
- **Tool definitions (examples):**  
  - `sales_order` — date range, product, plant, region.  
  - `dispatch` — same.  
  - `production` — same.  
  - `summary` — date; may call multiple tools and aggregate.  
  - `comparison` — two date ranges or two metrics; call APIs and compare in response.
- **Guardrail:** LLM for response generation must not receive any context other than user question and tool outputs; system prompt instructs “answer only from the provided data”.

---

## 14. Intent/Entity Extraction Design

- **Intents (examples):** `sales_order`, `dispatch`, `production`, `summary`, `comparison`, `trend`, `top_bottom`, `unsupported`.
- **Entities:** `date` (today, yesterday, this week, this month, explicit date), `product` (clinker, OPC, PPC), `plant`, `region`, `metric` (e.g. quantity only; value is not in the API).
- **Approach:**  
  - **Option A:** LLM with structured output (JSON schema) for intent + entities. Fast and flexible for Nepali/English mix.  
  - **Option B:** Rule-based + keywords for high-confidence cases; LLM fallback for the rest.  
  - **Option C:** Small fine-tuned model for intent/entity only (later phase).
- **Normalization:** Map “kati cha”, “how much”, “today” to canonical entities; normalize date to server date or user timezone if applicable.
- **Validation:** Reject or re-prompt if required entity is missing (e.g. “which product?” when APIs require it).

---

## 15. Internal API Integration Design

- **Contract:** Assistant Service calls internal APIs via server-side HTTP (or internal SDK). APIs return JSON; contract must be stable (versioned if needed). **Real endpoint catalog:** see [internal-api-catalog.md](internal-api-catalog.md).
- **Emp portal APIs (e.g. Sales Force returnData):** Call `GET /HRMS/SalesForce/returnData?ABC=108` with required headers (see [internal-api-catalog.md](internal-api-catalog.md)). **Response:** array of objects with `Description…` (metric label), `______Type_____` (metric type), `Quantity` (numeric), and `___Value____` (amount). The assistant must normalize these into `description`, `metric_type`, and `quantity` only, ignore value/amount, and answer **only** from those fields; add/subtract or aggregation is done in your backend from `quantity` values.
- **Mapping:** Tool layer maps intent + entities to API query params (e.g. `ABC=108` for ChatBot metrics, or another report ID / filters if you add more endpoints), plus any additional filters such as `product=OPC`, `from=date`, `to=date`, `plant=…` where supported. Document mapping in code and in runbook.
- **Question → description check:** For APIs that return multiple rows with `Description_____`, the backend must **check the question**, decide which description(s) are relevant (e.g. today vs this month, OPC vs PPC), **filter** the API response to only those rows, then pass the filtered subset to the response generator. You can extend a **description registry** (see [internal-api-catalog.md](internal-api-catalog.md) and `config/description-registry.example.json`) as you add more APIs and labels so answers always match the question.
- **Idempotency / rate limits:** Respect existing API rate limits; no write operations.
- **Errors:** Map HTTP errors and empty results to clear internal codes (e.g. NO_DATA, API_ERROR). Response generator turns these into safe user-facing messages.
- **Timeouts:** Set timeouts (e.g. 5–8 s per API); on timeout, return “Data temporarily unavailable” and log.

---

## 16. Response Generation Rules and Anti-Hallucination Guardrails

- **Strict rule:** Response generator receives only: (1) user question, (2) tool results (and tool errors). No external knowledge base in context for numbers or facts.
- **Portal APIs (Sales Force returnData):** Response items have `Description_____` and `Quantity` only (value removed from API) (see [internal-api-catalog.md](internal-api-catalog.md)). After normalizing to description and quantity, the assistant must use **only** those fields. Do not use or refer to any value/amount field. Do not invent, add, or subtract numbers; any aggregation is done in your backend before passing results to the response generator.
- **System prompt:** “You are a business assistant. Answer ONLY using the data provided below. Do not add, assume, or infer any numbers or facts not present in the data. If the data is empty or insufficient, say so clearly and suggest what the user might ask.”
- **Templates option:** For high-frequency intents (e.g. “today dispatch”), optional template: “Today’s dispatch is {quantity} {unit} for {product}.” with blanks filled only from API response (e.g. from the `description` and `quantity` fields only). Reduces LLM drift.
- **Citation:** Optional “Based on Sales API” / “Based on Dispatch API” in UI to reinforce source.
- **Empty/error:** Never say “X is 0” unless API explicitly returned 0. Prefer “No data returned for this period” or “Data unavailable; please try again.”

---

## 17. Authentication and Authorization Integration

- **Authentication:** Reuse existing website mechanism (session cookie or JWT). Assistant API reads session and gets user identity (user_id, role). No separate login.
- **Authorization:**  
  - **Drawer visibility:** Frontend checks feature flag or role (e.g. “assistant.enabled”) to show/hide trigger.  
  - **Backend:** Assistant API verifies same role/permissions before processing; optionally restrict by plant/region if your RBAC supports it.  
- **Token propagation:** If internal APIs require a token, Assistant Service obtains it via existing server-side auth (e.g. service account or pass-through user token) and does not expose it to the client.

---

## 18. Audit Logging and Observability

- **Audit log (per request):** user_id, timestamp, raw question, normalized intent, entities, tools called, API response status (success/error), response length or hash, and no PII in payload. Store in DB or append-only store; retain per policy.
- **Application logs:** Request ID, latency, errors (no sensitive payloads).
- **Metrics:** Request count by intent, latency p50/p95, error rate, tool call count. Expose via existing metrics system (e.g. Prometheus).
- **Optional:** Distributed tracing for “question → intent → tools → response” for debugging.

---

## 19. Data Model / Database Tables Needed

**Only for assistant-specific data (not for business data; that stays in existing systems):**

- **audit_logs (or assistant_audit_logs):** id, user_id, session_id, question_text, intent, entities_json, tools_called_json, response_summary_or_hash, status (success/partial/error), created_at. Index: user_id, created_at.
- **Optional – conversation_history (Phase 2):** id, user_id, conversation_id, role (user|assistant), content, created_at. Index: user_id, conversation_id, created_at.
- **Optional – feature_flags:** name, enabled, config_json. For assistant trigger type, voice on/off, TTS on/off, etc.

No duplication of Sales Order, Dispatch, or Production data; those remain in existing systems and are accessed via APIs only.

---

## 20. Error Handling and Fallback Behavior

| Scenario | Behavior |
|----------|----------|
| User sends empty message | Ignore or prompt “Please type or say your question.” |
| Intent unclear | Ask one short clarifying question (e.g. “Which product: Clinker, OPC, or PPC?”). |
| One API times out | Return partial answer with note: “Dispatch data is temporarily unavailable.” |
| All APIs fail | “We couldn’t fetch data right now. Please try again in a few minutes.” + log. |
| LLM unavailable | Fallback: “Assistant is temporarily unavailable. Please try again.” + retry logic. |
| Unsupported question | “I can only help with sales orders, dispatch, and production. Try: ‘Today’s dispatch’ or ‘This month’s clinker sales.’” |
| TTS/STT unsupported or fails | Hide voice/TTS controls or show “Voice not available in this browser.” |

---

## 21. Security Considerations

- **Input:** Sanitize and length-limit user message; no script injection in stored or displayed content.
- **Output:** Escape assistant response for the UI (e.g. no raw HTML from LLM).
- **API keys / secrets:** Only in backend env; never in frontend.
- **Rate limiting:** Per user or per session to avoid abuse (e.g. 30 requests/minute).
- **RBAC:** Enforce at API layer; do not rely only on UI hiding.
- **Audit:** Log access and failures; protect audit log storage.

---

## 22. Performance and Caching Strategy

- **Caching:** Optional short TTL cache (e.g. 1–2 min) for identical intent+entity+date (e.g. “today dispatch”) to reduce duplicate API and LLM calls. Invalidate by time or explicit refresh.
- **Connection pooling:** Use connection pooling for internal API and DB (if any).
- **Async:** Run independent tool calls in parallel where possible (e.g. order + dispatch + production for “today summary”).
- **Frontend:** Lazy-load drawer content; keep bundle small.

---

## 23. Deployment Architecture

- **Frontend:** Deployed with existing website (same build/release). Feature flag controls visibility.
- **Backend:** Assistant API and Assistant Service can be same process as existing API or a separate service (e.g. Node or Python) behind same API gateway. Same network as internal APIs to avoid public exposure.
- **LLM:** Use existing or new LLM endpoint (e.g. Azure OpenAI, OpenAI, or on-prem). Prefer same region/low latency.
- **Secrets:** From existing secret manager (e.g. env vars or vault). No secrets in repo.

---

## 24. Phase-Wise Implementation Roadmap

| Phase | Scope | Deliverable |
|-------|--------|-------------|
| **Phase 1 – Core** | Drawer UI, text input, intent/entity, 3 tools (order, dispatch, production), response from API only, audit log, auth/RBAC. | Leadership can ask typed questions and get correct, sourced answers. |
| **Phase 2 – Voice & polish** | Voice input (STT), TTS for last reply, optional conversation persistence, error/fallback polish. | Full voice in/out and smoother UX. |
| **Phase 3 – Extended queries** | Summary (multi-API), comparison, trend, top/bottom (as APIs allow); optional caching. | “Today summary”, “today vs yesterday”, “top product this week.” |
| **Phase 4 – Scale & ops** | Rate limiting, metrics, runbooks, optional tracing; rollout to more users. | Production-hardened and observable. |

---

## 25. Engineering Task Breakdown

**Frontend:**  
- Add AssistantProvider + trigger (header or FAB).  
- Implement AssistantDrawer, Conversation, MessageBubble, InputArea.  
- Integrate postMessage API and loading/error states.  
- Add VoiceInput (STT) and TTSPlayer.  
- Accessibility: focus trap, ARIA, keyboard.  
- Tests: component tests for drawer and input; optional E2E for one happy path.

**Backend:**  
- Assistant API route: auth, RBAC, audit, call Assistant Service.  
- Assistant Service: intent extraction, tool registry, internal API client, response generator.  
- Implement 3 tools: sales order, dispatch, production (and later summary/comparison).  
- Unit tests for intent parsing, tool param mapping, response generator (no hallucination).  
- Integration tests: API → mock internal APIs → assert response content.

**DevOps / config:**  
- Feature flags (drawer, voice, TTS).  
- Audit table and logging pipeline.  
- Secrets and env for LLM and internal APIs.

---

## 26. Risks and Mitigation

| Risk | Mitigation |
|------|-------------|
| LLM hallucination | Strict prompt + only tool results in context; templates for critical intents; review samples. |
| Internal API instability | Timeouts, retries, graceful partial answers; monitor API health. |
| Nepali/English mix misparsed | Test with real queries; iterate on intent examples; optional keyword fallbacks. |
| Voice accuracy (STT) | Use supported languages; show transcript for user to correct before send. |
| Scope creep | Strict supported-query list and boundary message; new intents only after API support. |

---

## 27. Sample Conversation Flows

**Flow 1 – Typed, simple**  
- User: “Today sales order kati cha?”  
- Intent: sales_order; entities: date=today.  
- Tool: SalesOrderTool(today).  
- Response: “Today’s sales order total is X tonnes. [Breakdown by product if API provides it.]”  
- User: [Read aloud] → TTS: “Today’s sales order total is X tonnes.”

**Flow 2 – Summary**  
- User: “Give me today summary.”  
- Intent: summary; entities: date=today.  
- Tools: SalesOrderTool, DispatchTool, ProductionTool (parallel).  
- Response: “Today’s summary: Sales order: X tonnes. Dispatch: Y tonnes. Production: Z tonnes.”  
- No invented numbers.

**Flow 3 – Missing data**  
- User: “Clinker production yesterday at Plant B.”  
- APIs return empty for that combination.  
- Response: “No production data returned for Clinker at Plant B for yesterday. Please check the date and plant, or try a different filter.”

**Flow 4 – Unsupported**  
- User: “What’s the weather?”  
- Intent: unsupported.  
- Response: “I can only help with sales orders, dispatch, and production. Try: ‘Today’s dispatch’ or ‘This month’s clinker sales order.’”

---

## 28. Suggested Folder Structure (Frontend and Backend)

**Assumption:** Monorepo or separate repos; structure is conceptual. Adapt to your existing layout.

**Frontend (e.g. existing app with React):**

```
src/
  features/
    assistant/
      components/
        AssistantDrawer.tsx
        AssistantTrigger.tsx
        Conversation.tsx
        MessageBubble.tsx
        InputArea.tsx
        VoiceInput.tsx
        TTSPlayer.tsx
      context/
        AssistantProvider.tsx
      hooks/
        useAssistant.ts
        useVoiceInput.ts
      api/
        assistantApi.ts
      types.ts
```

**Backend (e.g. Node or Python):**

```
backend/
  assistant/
    api/
      assistantRoutes.ts   # POST /chat, auth, audit
    service/
      AssistantService.ts
      intent/
        IntentExtractor.ts
        entities.ts
      tools/
        ToolRegistry.ts
        SalesOrderTool.ts
        DispatchTool.ts
        ProductionTool.ts
      InternalApiClient.ts
      ResponseGenerator.ts
    prompts/
      systemPrompts.ts
    config/
      featureFlags.ts
  middleware/
    auth.ts
    rbac.ts
  audit/
    auditLogger.ts
  lib/
    llmClient.ts
```

**Shared / config:**

```
docs/
  PRODUCTION_ASSISTANT_DESIGN.md  # this document
  assistant-api.md                # API contract
config/
  featureFlags.example.json
```

---

## 29. Rollout Plan for Production

1. **Feature flag:** Ship drawer and backend behind flag; default off.  
2. **Internal pilot:** Enable for 2–3 leadership users; collect feedback on intents and phrasing.  
3. **Iterate:** Fix misparsed intents and response wording; add missing entity handling.  
4. **Soft launch:** Enable for all leadership; monitor audit logs and errors.  
5. **Documentation:** Short internal guide: “How to ask” and supported query types.  
6. **Support:** Designate owner for “assistant down” or “wrong answer”; runbook for common failures.  
7. **Rollback:** Disable feature flag to hide drawer and return 503 or graceful message from API.

---

## 30. Future Enhancements

- **More data sources:** Inventory, quality, or finance APIs as they become available.  
- **Scheduled briefings:** “Send me daily summary at 8 AM” (email or in-app).  
- **Alerts:** “Notify me when dispatch &gt; X” (with guardrails and rate limits).  
- **Multi-plant / group view:** If group-level APIs exist.  
- **Export:** PDF or Excel of the last answer.  
- **Conversation memory:** Optional multi-turn context (“and yesterday?” referring to previous product).  
- **Stricter compliance:** Optional PII redaction in logs or retention policy for audit table.

---

**End of design document.**  
Next step: Align with your existing website stack (framework, auth, API base) and internal API contracts, then implement Phase 1 per the task breakdown and folder structure above.
