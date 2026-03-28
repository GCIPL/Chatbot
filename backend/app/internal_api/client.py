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

# Same dashboard as portal "ChatBothLink" (grid loads returnData?ABC=109).
CHATBOT_LINKS_REFERER = (
    "https://emp-portal.ghorahicement.com/Hrms/SalesForce/Dashboard?DashboardName=ChatBothLink"
)


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
    Map API rows to description + quantity + metric_type.

    API returns columns: Description, Type, Quantity.
    - Description: e.g. "Today SO (NP) PPC", "Today Sales Dispatch(NP) OPC", "Stock Qnty", etc.
    - Type: e.g. "SO Qnty in MT", "Sales Dispatch Qnty in MT", "Stock Qnty", "Received Qnty in (Nos.)", "Production Qnty MT", "Attendance".
    - Quantity: the numeric quantity only (MT, Nos., Ltr., Kg., etc.). Do not use any "Value" or amount column — quantity only.
    Also accepts legacy keys (Item/Description, Status/Metric Type) or alternate casing. We never read "Value" — only "Quantity".
    """
    out: list[NormalizedRow] = []

    for row in raw:
        desc = None
        metric_type_raw = None
        qty = None

        for k, v in row.items():
            base = k.strip("_").lower().replace(" ", "").replace("/", "")
            if v is None or v == "":
                continue
            # Description column: "Description", "Item/Description", "Item"
            if base in ("description", "itemdescription", "item"):
                desc = (v or "").strip() if isinstance(v, str) else str(v).strip()
            # Metric type column: "type", "Status/Metric Type", "Status", "Metric Type"
            elif base in ("type", "statusmetrictype", "status", "metrictype"):
                metric_type_raw = (v or "").strip() if isinstance(v, str) else str(v).strip()
            # Quantity column only (do not use "Value" or amount)
            elif base == "quantity":
                qty = v

        if desc is None:
            desc = (row.get("description") or row.get("Description") or "").strip()
        if metric_type_raw is None:
            metric_type_raw = (row.get("type") or row.get("Type") or "").strip()
        if qty is None:
            qty = row.get("Quantity") or row.get("quantity")

        if qty is None:
            continue
        try:
            qty_float = float(qty)
        except (TypeError, ValueError):
            continue
        metric_type = metric_type_raw or None
        if metric_type is not None and not metric_type:
            metric_type = None
        out.append(
            NormalizedRow(
                description=desc or "",
                quantity=qty_float,
                metric_type=metric_type,
            )
        )
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


def _normalize_quick_link_rows(raw: list[dict[str, Any]]) -> list[dict[str, str]]:
    """
    ChatBothLink API (returnData?ABC=chatbot_links) returns objects like:
    {"Name": "...", "Web_Excel_Address": "https://..."} — not metric rows.
    """
    out: list[dict[str, str]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        name = ""
        url = ""
        for k, v in row.items():
            if v is None or v == "":
                continue
            ks = k.strip("_").lower().replace(" ", "")
            vs = v.strip() if isinstance(v, str) else str(v).strip()
            if not vs:
                continue
            if ks == "name":
                name = vs
            elif ks in ("webexceladdress", "web_excel_address"):
                url = vs
        if name and url.startswith(("http://", "https://")):
            out.append({"name": name, "url": url})
    return out


async def fetch_chatbot_quick_links(
    session_cookie: str | None = None,
    timeout_seconds: float = 10.0,
) -> list[dict[str, str]]:
    """
    GET /HRMS/SalesForce/returnData?ABC=sales_force_abc_chatbot_links
    Referer must match ChatBothLink dashboard (same as portal grid).
    """
    url = f"{settings.emp_portal_base_url.rstrip('/')}/HRMS/SalesForce/returnData"
    params = {"ABC": settings.sales_force_abc_chatbot_links}
    headers = dict(EMP_PORTAL_HEADERS)
    headers["Referer"] = CHATBOT_LINKS_REFERER
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
    return _normalize_quick_link_rows(raw)
