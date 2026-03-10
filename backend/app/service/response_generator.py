"""Generate reply only from tool results. No value/amount; description + quantity only."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.models import NormalizedRow
from app.prompts import RESPONSE_SYSTEM, format_tool_results_for_llm
from app.service.llm import get_llm


CAPABILITIES_TEXT = """I can provide data in the following categories:

1. Category: Sales
2. Category: Production
3. Category: Attendance
4. Category: Stock
5. Category: Received

Please specify which category or specific data you are interested in."""


def _is_capabilities_question(question: str) -> bool:
    q = (question or "").lower()
    keywords = [
        "what can you do",
        "what you can do",
        "what information can you provide",
        "what information can you give",
        "what data can you provide",
        "what data you can provide",
        "what things you can give",
        "ke ke dina sakchhau",
        "ke ke dinchhau",
        "what all can you provide",
        "what all can you do",
    ]
    return any(k in q for k in keywords)


async def generate_reply(
    question: str,
    rows: list[NormalizedRow],
) -> tuple[str, str | None]:
    """
    Generate reply and optional short reply_for_tts.
    LLM sees only question and the formatted rows (description + quantity),
    except for capabilities questions which use a fixed text response.
    """
    # Capabilities intent: describe what information is available.
    if _is_capabilities_question(question):
        return CAPABILITIES_TEXT, "I can provide sales, production, attendance, stock, and received data."
    if not rows:
        return (
            "No data returned for this query. Try asking for today, this month, or this year (e.g. 'Today sales kati cha?').",
            None,
        )

    data_block = format_tool_results_for_llm(rows)
    user_content = f"User question: {question}\n\nData (description and quantity only; no value):\n{data_block}"

    llm = get_llm()
    if llm is None:
        lines = [f"{r.description}: {r.quantity}" for r in rows[:10]]
        if len(rows) > 10:
            lines.append(f"... and {len(rows) - 10} more rows.")
        return "\n".join(lines), None

    messages = [
        SystemMessage(content=RESPONSE_SYSTEM),
        HumanMessage(content=user_content),
    ]
    try:
        response = await llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        reply = (content or "").strip()
    except Exception:
        # 429 quota or other LLM errors: fall back to raw data
        lines = [f"{r.description}: {r.quantity}" for r in rows[:15]]
        if len(rows) > 15:
            lines.append(f"... and {len(rows) - 15} more.")
        return "\n".join(lines), None
    # Short version for TTS: first sentence or first 100 chars
    reply_for_tts = None
    if reply:
        for sep in (". ", "। "):
            if sep in reply:
                reply_for_tts = reply.split(sep)[0].strip() + (sep.strip() or ".")
                break
        if not reply_for_tts:
            reply_for_tts = reply[:120] + ("..." if len(reply) > 120 else "")
    return reply, reply_for_tts
