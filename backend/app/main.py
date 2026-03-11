"""FastAPI app: Ghorahi Cement Assistant backend."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.assistant import router as assistant_router

# UI is served from static/ (filled in Docker build from demo/chat.html)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: compile graph once (optional, can be lazy)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Ghorahi Cement Assistant API",
    description="Embedded enterprise assistant: intent → tools → response. Description + quantity only; no value.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assistant_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Serve the chat UI so the same Cloud Run URL has both UI and API."""
    index = STATIC_DIR / "index.html"
    if not index.exists():
        return {"message": "Ghorahi Assistant API", "ui": "Not bundled. Use /api/assistant/chat."}
    return FileResponse(index, media_type="text/html")


@app.get("/chat.html")
async def chat_page():
    """Serve the chat UI (same as /)."""
    index = STATIC_DIR / "index.html"
    if not index.exists():
        return {"message": "UI not bundled."}
    return FileResponse(index, media_type="text/html")
