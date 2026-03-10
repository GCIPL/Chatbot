"""LangGraph: intent → tools → response. State is dict; only tool results go to response."""
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.config import settings
from app.models import ToolResult
from app.service.intent import extract_intent_and_entities
from app.service.response_generator import generate_reply
from app.service.tools import all_normalized_rows, run_sales_force_tool


class AssistantStateDict(TypedDict, total=False):
    question: str
    session_cookie: str | None
    intent_result: dict[str, Any]
    tool_results: list[dict[str, Any]]
    reply: str
    reply_for_tts: str | None
    sources: list[str]


def _get_registry_path() -> Path | None:
    try:
        return settings.description_registry_path()
    except Exception:
        return None


async def _node_extract_intent(state: AssistantStateDict) -> AssistantStateDict:
    question = state.get("question") or ""
    intent_result = await extract_intent_and_entities(question)
    return {"intent_result": intent_result.model_dump()}


async def _node_run_tools(state: AssistantStateDict) -> AssistantStateDict:
    question = state.get("question") or ""
    session_cookie = state.get("session_cookie")
    registry_path = _get_registry_path()

    # Currently one tool: sales_force. Add dispatch/production when you have APIs.
    result = await run_sales_force_tool(
        question=question,
        session_cookie=session_cookie,
        registry_path=registry_path,
    )
    return {"tool_results": [result.model_dump()]}


async def _node_generate_response(state: AssistantStateDict) -> AssistantStateDict:
    question = state.get("question") or ""
    tool_results_raw = state.get("tool_results") or []
    tool_results = [ToolResult.model_validate(r) for r in tool_results_raw]
    rows = all_normalized_rows(tool_results)

    reply, reply_for_tts = await generate_reply(question, rows)
    sources = list({tr.tool_name for tr in tool_results if tr.success})

    return {
        "reply": reply,
        "reply_for_tts": reply_for_tts,
        "sources": sources,
    }


def build_assistant_graph() -> StateGraph:
    """Build the graph: extract_intent → run_tools → generate_response → END."""
    # State schema: optional fields for partial updates
    graph = StateGraph(AssistantStateDict)

    graph.add_node("extract_intent", _node_extract_intent)
    graph.add_node("run_tools", _node_run_tools)
    graph.add_node("generate_response", _node_generate_response)

    graph.set_entry_point("extract_intent")
    graph.add_edge("extract_intent", "run_tools")
    graph.add_edge("run_tools", "generate_response")
    graph.add_edge("generate_response", END)

    return graph


_compiled_graph = None


def get_compiled_graph():
    """Compiled graph; create once and reuse."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_assistant_graph().compile()
    return _compiled_graph
