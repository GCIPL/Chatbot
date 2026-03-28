"""Assistant chat API: POST /api/assistant/chat."""
import json
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException

from app.internal_api.client import fetch_chatbot_quick_links
from app.models import ChatRequest, ChatResponse, QuickLinkItem, QuickLinksResponse
from app.service.graph import get_compiled_graph

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process one user message: intent → tools → response.
    Only description + quantity from APIs; no value.
    """
    graph = get_compiled_graph()
    initial: dict = {
        "question": request.message.strip(),
        "session_cookie": None,  # TODO: from request headers when frontend sends session
    }
    try:
        result = await graph.ainvoke(initial)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant error: {e}") from e

    reply = result.get("reply", "I couldn't generate a response.")
    reply_for_tts = result.get("reply_for_tts")
    sources = result.get("sources") or []

    return ChatResponse(
        reply=reply,
        reply_for_tts=reply_for_tts,
        sources=sources,
    )


@router.get("/quick-links", response_model=QuickLinksResponse)
async def quick_links():
    """
    Company portal shortcuts from the same source as the employee portal
    ChatBothLink dashboard (Sales Force returnData, ABC=109 by default).
    """
    try:
        raw = await fetch_chatbot_quick_links()
        return QuickLinksResponse(
            links=[QuickLinkItem(name=x["name"], url=x["url"]) for x in raw],
            error=None,
        )
    except httpx.HTTPError as e:
        return QuickLinksResponse(links=[], error=str(e)[:300])
    except Exception as e:
        return QuickLinksResponse(links=[], error=str(e)[:300])


def _portal_link_meta_path() -> Path:
    # backend/app/api/assistant.py -> parents[2] == backend root
    return Path(__file__).resolve().parents[2] / "config" / "portal-link-meta.json"


@router.get("/portal-link-meta")
async def portal_link_meta():
    """
    Grouping labels, keywords, and short descriptions for portal quick links UI.
    Edit backend/config/portal-link-meta.json to change themes and blurbs.
    """
    path = _portal_link_meta_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
