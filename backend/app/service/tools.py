"""Tools: call internal APIs and filter by question. Description + quantity only."""
from pathlib import Path

from app.internal_api.client import fetch_sales_force_return_data
from app.models import NormalizedRow, ToolResult
from app.service.description_filter import filter_rows_by_question


async def run_sales_force_tool(
    question: str,
    session_cookie: str | None = None,
    registry_path: Path | None = None,
) -> ToolResult:
    """
    Fetch Sales Force returnData, then filter rows by question (time/product).
    Returns only description + quantity; no value.
    """
    try:
        rows = await fetch_sales_force_return_data(session_cookie=session_cookie)
    except Exception as e:
        return ToolResult(
            tool_name="sales_force",
            success=False,
            rows=[],
            error=str(e),
        )

    # Determine category/domain from question text: sales, production, attendance, stock, received.
    # Default to sales for generic business questions.
    q = question.lower()
    domain = "sales"
    if any(word in q for word in ("attendance", "present", "employee", "staff")):
        domain = "attendance"
    elif any(word in q for word in ("stock", "inventory", "balance")):
        domain = "stock"
    elif any(word in q for word in ("received", "receipt", "receive")):
        domain = "received"
    elif any(word in q for word in ("production", "utpadan")):
        domain = "production"

    def type_matches(row: NormalizedRow) -> bool:
        mt = (row.metric_type or "").lower()
        if not mt:
            # If type is missing, keep the row only for very generic questions (domain == sales).
            return domain == "sales"

        if domain == "sales":
            return "sales" in mt
        if domain == "production":
            return "production" in mt
        if domain == "attendance":
            return "attendance" in mt
        if domain == "stock":
            return "stock" in mt
        if domain == "received":
            return "received" in mt
        return True

    # First, restrict rows by metric_type / domain.
    domain_rows: list[NormalizedRow] = [r for r in rows if type_matches(r)]

    # Then apply description-based time/product filtering.
    filtered = filter_rows_by_question(domain_rows, question, registry_path)
    return ToolResult(
        tool_name="sales_force",
        success=True,
        rows=filtered,
    )


def all_normalized_rows(tool_results: list[ToolResult]) -> list[NormalizedRow]:
    """Collect all successful rows from tool results."""
    out: list[NormalizedRow] = []
    for tr in tool_results:
        if tr.success and tr.rows:
            out.extend(tr.rows)
    return out
