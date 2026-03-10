# Internal API Catalog — Ghorahi Cement Employee Portal

This document describes the **real** internal APIs the assistant backend must call. The assistant must answer **only** from the fields documented here. No other numbers or labels may be used in the response.

**Status:** Sales Force `returnData?ABC=108` is the current ChatBot data source. The response shape below is **verified** from a live call (see \"Live response sample\").

**Extensible descriptions:** You can and will add more APIs and more `Description_____` values over time. The system must **check the question** → decide which description(s) are relevant → return answers **only** from those rows. See section "Question → description matching" below.

---

## 1. Sales Force / returnData (ChatBot metrics)

**Purpose:** Returns metrics for dashboards and the assistant. Today this includes:
- Sales quantities in MT (Today, Current Month, Current FY; NP = domestic, EXP = export; OPC/PPC).
- Production quantities in MT (e.g. clinker, fine coal, raw meal, semi-finished cement by line).
- Stock quantities (e.g. HSD).
- Attendance / location style metrics (if configured).

**Base URL:** `https://emp-portal.ghorahicement.com`

**Endpoint:** `GET /HRMS/SalesForce/returnData`

**Query parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `ABC`     | Yes      | Report ID. `108` = ChatBotData / consolidated metrics (current source for the assistant). |

**Request headers (backend must send):**

- `Accept: application/json, text/javascript, */*; q=0.01`
- `X-Requested-With: XMLHttpRequest`
- `Referer: https://emp-portal.ghorahicement.com/Hrms/SalesForce/Dashboard?DashboardName=SalesSummary`
- `User-Agent`: same as portal or a consistent server-side UA
- **Cookie:** Session cookie (e.g. `ASP.NET_SessionId=...`) when calling with user context. (Call succeeded without cookie in one test; production should still forward session.)

**Response shape (verified for ABC=108):**

- **Body:** Response body may be a **JSON string** (double-encoded). Backend should parse once: if `typeof body === 'string'`, run `JSON.parse(body)` to get the array.
- **Array of objects.** Each item has:

| Field              | Type   | Use in answer |
|--------------------|--------|----------------|
| `Description_______` / `Description_____` | string | **Yes** — Metric label (e.g. "Today(NP)  OPC ", "Current_Mth(EXP)  PPC ", "Current_Mth Clinker Line-2"). Trim spaces. |
| `______Type_____`  | string | **Yes** — Metric type, e.g. `"Sales Qnty in MT"`, `"Production Qnty MT"`, `"Stock Qnty"`, `"Attendance Manoj"`. Used to decide domain (sales vs production vs stock vs attendance) and unit (MT vs other). |
| `Quantity`         | number | **Yes** — Quantity used in answers (e.g. tonnes, MT, counts). All calculations are based on this field only. |
| `___Value____`     | number | **No** — Value/amount field. **Ignored** by the assistant for safety; not used in any calculations or answers. |

**Assistant rule:** Use **only** Description, Type, and Quantity from each row. Do not invent or add/subtract numbers beyond sums/differences of `Quantity`. Do **not** use or expose `___Value____` in answers.

**Live response sample (ABC=108) — truncated:**

```json
[
  {
    "Description_______": "Today(NP)  OPC ",
    "______Type_____": "Sales Qnty in MT",
    "Quantity": 376,
    "___Value____": 4624963.0
  },
  {
    "Description_______": "Today(NP)  PPC ",
    "______Type_____": "Sales Qnty in MT",
    "Quantity": 367,
    "___Value____": 3811392.0
  },
  {
    "Description_______": "Current_Mth(EXP)  OPC ",
    "______Type_____": "Sales Qnty in MT",
    "Quantity": 2650,
    "___Value____": 18222098.0
  },
  {
    "Description_______": "Yesterday Clinker Line-2",
    "______Type_____": "Production Qnty MT",
    "Quantity": 6735,
    "___Value____": 0.0
  },
  {
    "Description_______": "Stock HSD",
    "______Type_____": "Stock Qnty",
    "Quantity": 0,
    "___Value____": 25000.0
  }
  // ... more rows ...
]
```

**Backend normalization (recommended):** When passing data to the response generator, normalize keys to avoid confusion and keep only what the assistant needs:

```js
items.map(row => ({
  description: (row.Description_______ || row.Description_____ || '').trim(),
  quantity: row.Quantity,
  metric_type: (row.______Type_____ || row.type || '').trim() || null
}));
```

**Curl reference:**

```bash
curl 'https://emp-portal.ghorahicement.com/HRMS/SalesForce/returnData?ABC=108' \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Referer: https://emp-portal.ghorahicement.com/Hrms/SalesForce/Dashboard?DashboardName=ChatBotData' \
  -b 'ASP.NET_SessionId=<session_id>'
```

---

## 2. Question → description matching

**Goal:** According to the user's question, the system should **check** which description(s) apply and **give answers only from those**.

**Flow:**

1. User asks a question (e.g. "Today sales order kati cha?", "This month OPC only", "Dispatch today").
2. Backend infers from the question: **which API** to call (e.g. `returnData?ABC=108` or another ABC you add), **which time scope** (today / this month / this FY), **which product/type** (OPC / PPC / NP / Exp / all).
3. Backend calls the API, then **filters** the returned rows: keep only rows whose `Description_____` matches what the question asked for.
4. Backend passes **only those filtered rows** (description + quantity) to the response generator.
5. Assistant answers **only** from that subset — no other numbers.

**Matching rules (you maintain as you add more descriptions):**

- **Time in question** → filter by text in `Description_____`: "today"/"aaja" → `Today`; "this month"/"mahina" → `Current_Mth`; "this year"/"FY" → `Current_FY`.
- **Product in question** → filter by text in `Description_____`: "OPC" → rows with `OPC`; "PPC" → `PPC`; "NP"/"domestic" → `(NP)`; "export" → `(Exp)`.
- If the question doesn't specify (e.g. "today summary"), pass all matching time rows so the assistant can summarize.

**Description registry (optional):** Keep a config or table listing description patterns your APIs return. As you add more APIs or labels, add entries there so the backend can map question → which descriptions to use. Example:

| Question hint (time) | Description contains |
|----------------------|----------------------|
| today | Today |
| this month | Current_Mth |
| this year / FY | Current_FY |

| Question hint (product) | Description contains |
|-------------------------|----------------------|
| OPC | OPC |
| PPC | PPC |
| domestic / NP | (NP) |
| export | (Exp) |

The backend filters rows by description before sending to the response generator. The assistant only sees data that matches the question.

---

## 3. More endpoints / descriptions (to be added by you)

As you add more APIs (e.g. dispatch-only, production-only, different `ABC` or paths) or more report types with new `Description_____` values:

1. Add the endpoint and response shape to this catalog (same format as section 1).
2. Add the new description patterns and question hints to the question → description matching table or config above.
3. Rule stays: assistant answers **only** from the fields and rows that match the question.
