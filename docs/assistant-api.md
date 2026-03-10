# Assistant API Contract

Used by the frontend chat drawer to send messages and receive replies. All requests require existing website authentication (session cookie or Bearer token as per current site).

## Endpoint

```
POST /api/assistant/chat
```

## Request

**Headers:**

- `Content-Type: application/json`
- Existing auth header or cookie (e.g. `Cookie: session=...` or `Authorization: Bearer ...`)

**Body:**

```json
{
  "message": "Today sales order kati cha?",
  "conversationId": "optional-uuid-for-history-phase-2"
}
```

| Field            | Type   | Required | Description                                      |
|------------------|--------|----------|--------------------------------------------------|
| message          | string | Yes      | User message (text or STT transcript). Max length e.g. 2000. |
| conversationId   | string | No       | For future conversation persistence.            |

## Response

**Success (200):**

```json
{
  "reply": "Today's sales order total is 450 tonnes. Clinker: 200, OPC: 150, PPC: 100.",
  "replyForTts": "Today's sales order total is 450 tonnes.",
  "sources": ["Sales Order API"]
}
```

| Field       | Type     | Description                                      |
|------------|----------|--------------------------------------------------|
| reply      | string   | Full on-screen response (may include structure). |
| replyForTts| string   | Optional short version for TTS.                  |
| sources    | string[] | Optional list of APIs used.                      |

**Error (4xx/5xx):**

- **401:** Unauthorized (no/invalid session).
- **403:** Forbidden (role cannot use assistant).
- **429:** Too many requests (rate limit).
- **500:** Server error; client should show generic “Please try again” and retry.

```json
{
  "error": "assistant_unavailable",
  "message": "Assistant is temporarily unavailable. Please try again."
}
```

## Rate limit

Example: 30 requests per user per minute. Response `429` with `Retry-After` header when exceeded.
