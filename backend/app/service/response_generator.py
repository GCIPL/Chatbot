"""Generate reply only from tool results. No value/amount; description + quantity only."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.models import NormalizedRow
from app.prompts import RESPONSE_SYSTEM, format_tool_results_for_llm
from app.service.llm import get_llm


CAPABILITIES_TEXT = """I can provide data in the following categories:

1. Category: Sales (sales dispatch / actual sales)
2. Category: Sales Order (orders only; different from sales dispatch)
3. Category: Production
4. Category: Attendance
5. Category: Stock
6. Category: Received

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


def _try_generate_structured_sales_reply(
    question: str, rows: list[NormalizedRow]
) -> tuple[str, str | None] | None:
    """
    For Sales / Sales Order questions, generate a fully deterministic numeric reply
    so OPC, PPC, Nepal Total, Export Total, and Overall Total are always consistent
    with the underlying rows (no LLM arithmetic).
    """
    if not rows:
        return None

    # Detect sales vs sales order from metric_type
    mt_values = [(r.metric_type or "").lower() for r in rows if r.metric_type]
    is_sales_order = any("sales order" in mt or "so qnty" in mt for mt in mt_values)
    is_sales = any("sales dispatch" in mt for mt in mt_values)
    if not (is_sales or is_sales_order):
        return None

    # Aggregate by NP/EXP and OPC/PPC based on description text.
    nepal_opc = nepal_ppc = 0.0
    export_opc = export_ppc = 0.0
    any_export_rows = False

    for r in rows:
        desc = (r.description or "").lower()
        qty = float(r.quantity or 0.0)

        is_np = "(np" in desc or " np" in desc
        is_exp = "(exp" in desc or " exp" in desc
        is_opc = "opc" in desc
        is_ppc = "ppc" in desc

        if is_exp:
            any_export_rows = True
            if is_opc:
                export_opc += qty
            elif is_ppc:
                export_ppc += qty
            continue

        # Default bucket: treat as Nepal domestic if not explicitly EXP.
        if is_opc:
            nepal_opc += qty
        elif is_ppc:
            nepal_ppc += qty

    nepal_total = nepal_opc + nepal_ppc
    export_total = export_opc + export_ppc
    overall_total = nepal_total + export_total

    def fmt(x: float) -> str:
        # Format whole numbers without .0, with commas for readability
        if x == int(x):
            return f"{int(x):,}"
        return f"{x:,.2f}"

    category = "Sales Order" if is_sales_order else "Sales"
    header_line = f"Answer: Category: {category}"

    lines: list[str] = [header_line, "", "bifurcation:"]
    # OPC / PPC are Nepal domestic by default
    lines.append(f"- OPC: {fmt(nepal_opc)}MT")
    lines.append(f"- PPC: {fmt(nepal_ppc)}MT")
    lines.append(f"- Nepal Total: {fmt(nepal_total)}MT")
    if any_export_rows and export_total > 0:
        lines.append(f"- Export Total: {fmt(export_total)}MT")
    elif any_export_rows:
        lines.append("- Export Total: Export data unavailable")
    else:
        lines.append("- Export Total: Export data unavailable")
    lines.append(f"- Overall Total: {fmt(overall_total)}MT")

    reply = "\n".join(lines)
    # Short TTS summary
    reply_for_tts = f"{category}: Overall Total {fmt(overall_total)}MT."
    return reply, reply_for_tts


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
        return CAPABILITIES_TEXT, "I can provide sales, sales order, production, attendance, stock, and received data."
    if not rows:
        return (
            "No data returned for this query. Try asking for today, this month, or this year (e.g. 'Today sales kati cha?').",
            None,
        )

    # Deterministic numeric path for sales / sales order so arithmetic is guaranteed correct.
    structured_sales = _try_generate_structured_sales_reply(question, rows)
    if structured_sales is not None:
        return structured_sales

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
