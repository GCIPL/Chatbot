#!/usr/bin/env python3
"""
Run all 15 sample questions against the full API-shaped data and validate
answers against expected quantities. Fix: ensure only Quantity is used, time filter correct.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.internal_api.client import _normalize_rows
from app.service.tools import run_sales_force_tool

# Sample questions from demo/chat.html
SAMPLE_QUESTIONS = [
    "Today sales (dispatch)?",
    "This month sales (dispatch)?",
    "This year sales (dispatch)?",
    "Today sales order?",
    "This month sales order?",
    "Aaja production kati cha?",
    "Yo mahina production kati cha?",
    "Yo barsa production kati cha?",
    "Aaja raw material kati receive bhayo?",
    "Yo mahina raw material kati receive bhayo?",
    "Yo barsa raw material kati receive bhayo?",
    "Clinker stock, Empty bag stock ra Coal stock kati cha?",
    "Aaja attendance kati cha?",
    "What information can you provide?",
]


def extract_quantity_from_reply(reply: str, label: str) -> float | None:
    """Parse a number from reply e.g. 'OPC: 1174MT' or 'Overall Total: 1770MT'."""
    if not reply:
        return None
    # Match "label: 123MT" or "label: 1,234MT" or "label: 123"
    patterns = [
        rf"{re.escape(label)}\s*:\s*([\d,]+(?:\.\d+)?)\s*MT",
        rf"{re.escape(label)}\s*:\s*([\d,]+(?:\.\d+)?)",
    ]
    for pat in patterns:
        m = re.search(pat, reply, re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", ""))
    return None


async def main():
    data_path = Path(__file__).parent / "sample_api_data.json"
    with open(data_path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = _normalize_rows(raw)
    async def mock_fetch(*args, **kwargs):
        return rows

    import app.service.tools as tools_mod
    tools_mod.fetch_sales_force_return_data = mock_fetch

    from app.service.graph import get_compiled_graph
    graph = get_compiled_graph()

    errors = []
    for i, question in enumerate(SAMPLE_QUESTIONS, 1):
        try:
            out = await graph.ainvoke({"question": question})
            reply = (out.get("reply") or "").strip()
            if not reply:
                errors.append((i, question, "empty reply"))
                continue

            # Validations based on sample data (Description, Type, Quantity only)
            if "Today sales (dispatch)" in question or question == "Today sales (dispatch)?":
                # Today Sales Dispatch: 596+894+280 = 1770
                total = extract_quantity_from_reply(reply, "Overall Total") or extract_quantity_from_reply(reply, "Answer")
                if total is not None and abs(total - 1770) > 1:
                    errors.append((i, question, f"expected Today dispatch total 1770, got {total}"))
            if "Today sales order" in question:
                # Today SO: 1241+1110+742 = 3093
                total = extract_quantity_from_reply(reply, "Overall Total") or extract_quantity_from_reply(reply, "Answer")
                if total is not None and abs(total - 3093) > 1:
                    errors.append((i, question, f"expected Today SO total 3093, got {total}"))
            if "This year sales" in question:
                # Current_FY Sales Dispatch: 122201+132870+343+28857 = 284271
                total = extract_quantity_from_reply(reply, "Overall Total") or extract_quantity_from_reply(reply, "Answer")
                if total is not None and abs(total - 284271) > 1:
                    errors.append((i, question, f"expected FY dispatch total 284271, got {total}"))
            if "Aaja attendance" in question:
                # 35 + 143 = 178
                if "35" not in reply or "143" not in reply:
                    errors.append((i, question, "expected 35 and 143 in attendance reply"))
        except Exception as e:
            errors.append((i, question, str(e)[:120]))

    # Report
    print("Sample questions run: %d" % len(SAMPLE_QUESTIONS))
    if errors:
        print("Issues found:")
        for i, q, msg in errors:
            print("  %2d. %s -> %s" % (i, q[:50], msg))
        sys.exit(1)
    print("All validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
