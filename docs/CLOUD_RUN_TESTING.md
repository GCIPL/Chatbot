# Ghorahi Assistant – Cloud Run testing

## Live URL (UI + API)

**https://ghorahi-assistant-599117333117.asia-south1.run.app/**

Open in a browser to get the login screen, then the chat UI.

---

## Quick checks

| What | How |
|------|-----|
| **UI** | Open [the URL above](https://ghorahi-assistant-599117333117.asia-south1.run.app/) in a browser. You should see **Ghorahi Cement – AI Assistant Login**. |
| **Login** | Username: **gci**  Password: **gci** |
| **Health** | `curl https://ghorahi-assistant-599117333117.asia-south1.run.app/health` → `{"status":"ok"}` |
| **Chat API** | After login, click a sample question (e.g. **Today sales**) or type a question and send. |

---

## Test from command line

```bash
# Health
curl -sS "https://ghorahi-assistant-599117333117.asia-south1.run.app/health"

# Chat (capabilities question)
curl -sS -X POST "https://ghorahi-assistant-599117333117.asia-south1.run.app/api/assistant/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"What information can you provide?"}'

# Chat (today sales)
curl -sS -X POST "https://ghorahi-assistant-599117333117.asia-south1.run.app/api/assistant/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Today sales kati cha?"}'
```

---

## Env vars on Cloud Run

For full behaviour (OpenAI, emp-portal), set in **Cloud Run → ghorahi-assistant → Edit & deploy new revision → Variables & secrets**:

- `OPENAI_API_KEY`
- `LLM_PROVIDER` = `openai`
- `EMP_PORTAL_BASE_URL` = `https://emp-portal.ghorahicement.com`
- `SALES_FORCE_ABC` = `108`

Then redeploy the revision.
