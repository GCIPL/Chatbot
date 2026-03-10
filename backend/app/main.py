"""FastAPI app: Ghorahi Cement Assistant backend."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assistant import router as assistant_router


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
