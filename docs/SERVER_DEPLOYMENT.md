# Deploying on Your Server (Application Server Manager)

Use this when your files are hosted via an **application server manager** (IIS, Apache, Nginx, cPanel, Plesk, or similar). You need two things on the server: the **chat UI** (HTML) and the **assistant API** (backend).

---

## 1. What to put where

| Item | What it is | Where to put on server |
|------|------------|-------------------------|
| **Chat UI** | Single file: `demo/chat.html` | In your **web root** (e.g. `www`, `public_html`, `htdocs`, or the folder your server manager uses for “website files”). |
| **Backend API** | Python app (FastAPI) | Any folder on the server where you can run Python (e.g. `backend/` or a dedicated app directory). |

The chat page in the browser will **call your API** using the URL you set (or the same origin if you serve both from the same place).

---

## 2. Option A — UI and API on same server, same domain

**Setup:** Your server manager serves the website (e.g. `https://yoursite.com`). You want:
- `https://yoursite.com/chat.html` → the chat UI
- `https://yoursite.com/api/assistant/chat` → the backend API

**Steps:**

1. **Copy the chat UI**  
   - Upload `demo/chat.html` to your **web root** and name it `chat.html` (or put it in a subfolder, e.g. `assistant/chat.html`).

2. **Run the backend**  
   - On the server, run the Python backend (e.g. `cd backend && python run.py` or use gunicorn/uvicorn behind your server).  
   - Run it so it listens on a **local port** (e.g. `127.0.0.1:8000`).

3. **Point your server to the API**  
   - In your **application server manager** (or Nginx/Apache config), add a **reverse proxy** (or “proxy pass”) so that:
     - Requests to `https://yoursite.com/api/...` are forwarded to `http://127.0.0.1:8000/...`  
   - Example (Nginx):
     ```nginx
     location /api/ {
         proxy_pass http://127.0.0.1:8000/api/;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
     }
     ```
   - Example (Apache with mod_proxy):
     ```apache
     ProxyPass /api/ http://127.0.0.1:8000/api/
     ProxyPassReverse /api/ http://127.0.0.1:8000/api/
     ```

4. **Chat page**  
   - Open `https://yoursite.com/chat.html`.  
   - Leave the **API** field as the default (same origin), or set it to `https://yoursite.com`.  
   - The page will call `https://yoursite.com/api/assistant/chat`.

---

## 3. Option B — UI and API on same server, different paths/ports

**Setup:**  
- Chat UI is served by your server manager (e.g. `https://yoursite.com/chat.html`).  
- API runs on the same machine but on another port (e.g. `http://yoursite.com:8000` or a subdomain).

**Steps:**

1. **Copy the chat UI**  
   - Upload `demo/chat.html` to your web root (or the folder your server manager uses).

2. **Run the backend**  
   - On the server: `cd backend && python run.py` (or run uvicorn/gunicorn so the app listens on `0.0.0.0:8000`).  
   - If your manager or firewall allows it, port 8000 can be open so you can use `https://yoursite.com:8000`.

3. **Set API URL in the chat page**  
   - In `chat.html`, the “API” field is pre-filled from the page’s origin.  
   - If the API is on a different URL (e.g. `https://yoursite.com:8000` or `https://api.yoursite.com`), **change the API field** in the page to that URL (users can do it in the UI, or you can edit the default in the file before upload).

---

## 4. Option C — Only the UI on the server manager; API elsewhere (e.g. ngrok or local)

**Setup:**  
- Your **server manager** only serves the HTML (e.g. `https://yoursite.com/chat.html`).  
- The **API** runs somewhere else: e.g. your PC via ngrok (`https://xyz.ngrok.io`) or another server.

**Steps:**

1. **Copy the chat UI**  
   - Upload `demo/chat.html` to your web root (or the folder your server manager uses for website files).

2. **Run the API** where you want (e.g. your PC):  
   - `cd backend && python run.py`  
   - Expose it (e.g. `ngrok http 8000`) and note the URL (e.g. `https://abc123.ngrok.io`).

3. **Set API URL in the chat**  
   - When opening `https://yoursite.com/chat.html`, in the **API** field enter the API base URL (e.g. `https://abc123.ngrok.io`).  
   - The page will call `https://abc123.ngrok.io/api/assistant/chat`.

---

## 5. Files to upload to “website files” in server manager

- **Only one file is required for the UI:**  
  `demo/chat.html`  
  Copy it into the folder your application server manager uses for the site (often `www`, `public_html`, `htdocs`, or similar). You can rename it (e.g. `assistant.html`) or put it in a subfolder (e.g. `assistant/chat.html`).

**Backend** is not “uploaded” like static files: you deploy the `backend/` folder to the server and **run** it (Python + uvicorn/gunicorn), then either:
- proxy `/api/` to that process (Option A), or  
- open its port and point the chat “API” field to that URL (Option B/C).

---

## 6. Checklist

- [ ] `chat.html` is in the folder your server manager uses for website files.
- [ ] Backend is running on the server (or elsewhere) and reachable at the URL you use in the “API” field.
- [ ] If UI and API are on the same domain, a reverse proxy is set so `/api/` goes to the backend.
- [ ] You opened the chat page in the browser and set “API” to your backend URL if needed; then sent a test message.

If you tell me the **exact name** of your application server manager (e.g. IIS, cPanel, Plesk, “XAMPP”, etc.), the steps can be made more specific for that product.
