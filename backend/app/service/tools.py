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

    # Domains: sales = Sales Dispatch only (actual sales). sales_order = SO only (orders, not sales).
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
    elif any(
        word in q
        for word in (
            "sales order",
            "sales orders",
            " order ",
            " orders ",
            " so ",
            " so",
            "so?",
            "so only",
        )
    ):
        domain = "sales_order"

    def type_matches(row: NormalizedRow) -> bool:
        mt = (row.metric_type or "").lower()
        if not mt:
            return domain == "sales"

        # Sales = Sales Dispatch only (actual sales). Type e.g. "Sales Dispatch Qnty in MT".
        if domain == "sales":
            return "sales dispatch" in mt
        # Sales Order = SO only (orders). Type e.g. "SO Qnty in MT", "Sales Order Qnty in MT".
        if domain == "sales_order":
            return "so qnty" in mt or "sales order qnty" in mt
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

    # For stock, descriptions usually have no explicit time prefix (no "Today"/"Current_Mth").
    # Also, users often name specific items (clinker, empty bag, coal). For stock questions,
    # filter only by keywords in the description and do NOT apply time-based filtering.
    if domain == "stock":
        desc_q = q
        stock_keywords = []
        if "clinker" in desc_q:
            stock_keywords.append("clinker")
        if "empty bag" in desc_q or "emptybag" in desc_q or "bag" in desc_q:
            stock_keywords.append("empty bag")
        if "coal" in desc_q:
            stock_keywords.append("coal")

        if stock_keywords:
            lowered = [kw.lower() for kw in stock_keywords]
            filtered_rows: list[NormalizedRow] = []
            for r in domain_rows:
                d = r.description.lower()
                if any(kw in d for kw in lowered):
                    filtered_rows.append(r)
        else:
            filtered_rows = domain_rows
    else:
        # For non-stock domains, apply description-based time/product filtering.
        filtered_rows = filter_rows_by_question(domain_rows, question, registry_path)
    return ToolResult(
        tool_name="sales_force",
        success=True,
        rows=filtered_rows,
    )


def all_normalized_rows(tool_results: list[ToolResult]) -> list[NormalizedRow]:
    """Collect all successful rows from tool results."""
    out: list[NormalizedRow] = []
    for tr in tool_results:
        if tr.success and tr.rows:
            out.extend(tr.rows)
    return out
