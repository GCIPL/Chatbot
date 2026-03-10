# How to Give a Demo — Ghorahi Cement Assistant

## 1. Before the demo

**On your machine (or demo server):**

1. **Start the backend**
   ```bash
   cd backend
   source .venv/bin/activate   # or: .venv\Scripts\activate on Windows
   python run.py
   ```
   Wait until you see: `Uvicorn running on http://0.0.0.0:8000`

2. **Check it’s working**
   - Open: http://localhost:8000/health  
   - You should see: `{"status":"ok"}`

3. **Optional: open the demo page**  
   - Open `demo/chat-demo.html` in a browser (Chrome/Edge).  
   - Or use curl/Postman (see below).

---

## 2. Demo options

### Option A: Browser demo page (easiest)

1. Start the backend (step 1 above).
2. Open **`demo/chat-demo.html`** in Chrome or Edge (double‑click or File → Open).
3. Type a question and click **Send** (or press Enter).
4. Show the reply on the same page.

**Example questions to use:**

- Today sales kati cha?
- Give me today summary
- This month OPC sales
- Today dispatch

**If the demo page can’t reach the API:**  
- Backend must be running.  
- If the HTML file was opened from another machine, set the API URL in the page to your server (e.g. `http://YOUR_IP:8000`).

---

### Option B: Terminal (curl)

**One question:**
```bash
curl -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Today sales kati cha?"}'
```

**Pretty-print reply:**
```bash
curl -s -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Today sales kati cha?"}' | python3 -m json.tool
```

Good for showing “the API returns real data from our system.”

---

### Option C: Postman (or similar)

1. **Method:** POST  
2. **URL:** `http://localhost:8000/api/assistant/chat`  
3. **Headers:** `Content-Type: application/json`  
4. **Body (raw JSON):**
   ```json
   { "message": "Today sales kati cha?" }
   ```
5. Send and show the JSON response (reply, sources).

---

## 3. What to say in the demo

1. **Context:** “This is the Ghorahi Cement leadership assistant. It runs inside our existing website and answers only from our own data—no made‑up numbers.”
2. **Show a question:** e.g. “Today sales kati cha?” (English or Nepali).
3. **Show the answer:** “It called our Sales Force API, filtered by today, and returned only description and quantity.”
4. **Optional:** Show the **sources** field: e.g. `["sales_force"]` — “So we always know which system the answer came from.”

---

## 4. If something goes wrong

| Issue | What to do |
|-------|------------|
| Health returns 200 but chat fails | Check `.env`: `OPENAI_API_KEY` or `GEMINI_API_KEY`, and `LLM_PROVIDER=openai` if using OpenAI. |
| “Connection refused” in browser | Backend not running or wrong URL/port. Start with `python run.py` and use `http://localhost:8000` (or your server IP). |
| CORS error in browser | Use the provided `demo/chat-demo.html` (or ensure your frontend calls the same origin or the backend allows your origin). |
| Slow first reply | First request can be slow (LLM + emp‑portal API). Next ones are faster. |

---

## 5. Demo on another machine (e.g. colleague’s laptop)

1. Run the backend on **your** machine and note your IP (e.g. `192.168.1.10`).
2. Open `demo/chat-demo.html` on the **other** machine.
3. In the demo page, set **API base URL** to `http://YOUR_IP:8000` (no trailing slash).
4. Ensure their network can reach your machine on port 8000 (firewall/VPN as needed).
