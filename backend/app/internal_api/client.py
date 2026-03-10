"""HTTP client for emp-portal APIs. Description + quantity only; no value."""
import json
from typing import Any

import httpx

from app.config import settings
from app.models import NormalizedRow


EMP_PORTAL_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://emp-portal.ghorahicement.com/Hrms/SalesForce/Dashboard?DashboardName=SalesSummary",
    "User-Agent": "GhorahiAssistant/1.0",
}


def _parse_body(body: str | bytes) -> list[dict[str, Any]]:
    """Parse response; body may be double-encoded JSON string."""
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    data = json.loads(body)
    if isinstance(data, str):
        data = json.loads(data)
    return data if isinstance(data, list) else []


def _normalize_rows(raw: list[dict[str, Any]]) -> list[NormalizedRow]:
    """
    Map API rows to description + quantity + type (if present). No value.

    The emp-portal API uses keys like 'Description_____','Description_______',
    or even 'Description_____________' and similar for type/value. We strip
    underscores and match by base name so small schema changes don't break us.
    """
    out: list[NormalizedRow] = []

    for row in raw:
        desc_key = None
        type_key = None
        qty_key = None

        for k in row.keys():
            base = k.strip("_").lower()
            if base == "description":
                desc_key = k
            elif base in ("type", "______type_____".strip("_").lower()):
                type_key = k
            elif base == "quantity":
                qty_key = k

        desc = (row.get(desc_key) or row.get("description") or "").strip() if desc_key else (row.get("description") or "").strip()
        qty = row.get(qty_key) if qty_key else row.get("Quantity") or row.get("quantity")
        metric_type_raw = row.get(type_key) if type_key else row.get("type")
        metric_type = (metric_type_raw or "").strip() or None

        if qty is None:
            continue
        try:
            out.append(NormalizedRow(description=desc, quantity=float(qty), metric_type=metric_type))
        except (TypeError, ValueError):
            continue

    return out


async def fetch_sales_force_return_data(
    abc: str | None = None,
    session_cookie: str | None = None,
    timeout_seconds: float = 10.0,
) -> list[NormalizedRow]:
    """
    GET /HRMS/SalesForce/returnData?ABC=...
    Returns rows with description + quantity only. No value field used.
    """
    url = f"{settings.emp_portal_base_url.rstrip('/')}/HRMS/SalesForce/returnData"
    params = {"ABC": abc or settings.sales_force_abc}
    headers = dict(EMP_PORTAL_HEADERS)
    if session_cookie:
        headers["Cookie"] = session_cookie

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        resp = await client.get(url, params=params, headers=headers)

    if resp.status_code != 200:
        raise httpx.HTTPStatusError(
            f"Emp portal returned {resp.status_code}",
            request=resp.request,
            response=resp,
        )

    raw = _parse_body(resp.text)
    return _normalize_rows(raw)
