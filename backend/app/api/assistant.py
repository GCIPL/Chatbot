"""Assistant chat API: POST /api/assistant/chat."""
from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse
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
