# Assistant API Contract

Used by the frontend chat drawer to send messages and receive replies. All requests require existing website authentication (session cookie or Bearer token as per current site).

## Endpoints

```
POST /api/assistant/chat
GET  /api/assistant/quick-links
GET  /api/assistant/portal-link-meta
```

### GET `/api/assistant/portal-link-meta`

Returns JSON used by the chat UI to **group** navigation rows into sections (Sales, Dashboards, etc.). Source file: `backend/config/portal-link-meta.json`: `categoryOrder`, `categories` with `label` + `keywords` (matched against each link **name** from the portal). Optional `descriptions` (keyed by exact portal `Name`) is for future use; **link titles and URLs are never defined here** — they always come from `GET /api/assistant/quick-links`.

### GET `/api/assistant/quick-links`

Returns **company portal shortcuts** from the same source as the employee portal [ChatBothLink](https://emp-portal.ghorahicement.com/Hrms/SalesForce/Dashboard?DashboardName=ChatBothLink) dashboard (`/HRMS/SalesForce/returnData?ABC=109` by default: `Name` + `Web_Excel_Address`).

**Response (200):**

```json
{
  "links": [
    { "name": "Sales Summary", "url": "https://example.com/..." }
  ],
  "error": null
}
```

If the portal is unreachable, `links` may be empty and `error` may contain a short message.

---

## Chat endpoint

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

The API returns JSON with **snake_case** keys:

```json
{
  "reply": "Full on-screen response text (see examples below).",
  "reply_for_tts": "Short version for text-to-speech, or null.",
  "sources": ["sales_force"]
}
```

| Field          | Type     | Description                                      |
|----------------|----------|--------------------------------------------------|
| reply          | string   | Full on-screen response (may include structure). |
| reply_for_tts  | string \| null | Optional short version for TTS.             |
| sources        | string[] | List of tools used (e.g. `["sales_force"]`).     |

### Example responses (what the API returns)

**1. Sales (dispatch) — e.g. `"message": "Today sales (dispatch)?"`**

The API returns **today, monthly, and yearly** sales dispatch in one response (columns: Description, Type, Quantity). The **Description** prefix indicates the period:
- **Today** → `Today Sales Dispatch(NP) PPC`, `Today Sales Dispatch(NP) OPC`, `Today Sales Dispatch(EXP) OPC`
- **Monthly (month-to-date)** → `Current_Mth Sales Dispatch(NP) PPC`, etc.
- **Yearly (FY-to-date)** → `Current_FY Sales Dispatch(NP) PPC`, `Current_FY Sales Dispatch(EXP) OPC`, etc.

The backend filters by the period the user asked for (today / this month / this year), so "Today sales (dispatch)?" uses only rows whose description contains "Today". Numbers are whole integers (no `.0`).

```json
{
  "reply": "Answer: Category: Sales\n\nbifurcation:\n- OPC: 13520186MT\n- PPC: 6489971MT\n- Nepal Total: 17884716MT\n- Export Total: 2125441MT\n- Overall Total: 20010157MT",
  "reply_for_tts": "Answer: Category: Sales",
  "sources": ["sales_force"]
}
```

**2. Sales Order — e.g. `"message": "Today sales order?"`**

```json
{
  "reply": "Answer: Category: Sales Order\n\nbifurcation:\n- OPC: 1852MT\n- PPC: 1241MT\n- Nepal Total: 2351MT\n- Export Total: 742MT\n- Overall Total: 3093MT",
  "reply_for_tts": "Answer: Category: Sales Order",
  "sources": ["sales_force"]
}
```

**3. Production — e.g. `"message": "Aaja production kati cha?"`**

```json
{
  "reply": "Answer: Category: Production\n\nbifurcation:\n- PPC Cement (Semi Finished): 1296MT\n- OPC Cement 43 Grade (Semi Finished) (Line-2): 717MT",
  "reply_for_tts": "Answer: Category: Production",
  "sources": ["sales_force"]
}
```

**4. Attendance — e.g. `"message": "Aaja attendance kati cha?"`**

```json
{
  "reply": "Answer: Category: Attendance\n\nbifurcation:\n- Kathmandu Office: 35 headcount\n- Ghorahi Plant: 143 headcount",
  "reply_for_tts": "Answer: Category: Attendance",
  "sources": ["sales_force"]
}
```

**5. Stock — e.g. `"message": "Clinker stock kati cha?"`**

```json
{
  "reply": "Answer: Category: Stock\n\nClinker Line-2: 140137MT",
  "reply_for_tts": "Answer: Category: Stock",
  "sources": ["sales_force"]
}
```

**6. Received — e.g. `"message": "Today received Gypsum?"`**

```json
{
  "reply": "Answer: Category: Received\n\nToday received Gypsum: 119MT",
  "reply_for_tts": "Answer: Category: Received",
  "sources": ["sales_force"]
}
```

**7. Capabilities — e.g. `"message": "What information can you provide?"`**

```json
{
  "reply": "I can provide data in the following categories:\n\n1. Category: Sales (sales dispatch / actual sales)\n2. Category: Sales Order (orders only; different from sales dispatch)\n3. Category: Production\n4. Category: Attendance\n5. Category: Stock\n6. Category: Received\n\nPlease specify which category or specific data you are interested in.",
  "reply_for_tts": "I can provide sales, sales order, production, attendance, stock, and received data.",
  "sources": []
}
```

**8. No data / empty result**

```json
{
  "reply": "No data returned for this query. Try asking for today, this month, or this year (e.g. 'Today sales kati cha?').",
  "reply_for_tts": null,
  "sources": ["sales_force"]
}
```

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
