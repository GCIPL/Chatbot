#!/usr/bin/env python3
"""
Run 30 different questions against the sample API data.
Uses mocked fetch so no live API required. Run from backend/: python -m tests.run_30_questions
"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path so app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.internal_api.client import _normalize_rows, fetch_sales_force_return_data
from app.service.graph import get_compiled_graph


# 30 questions covering all categories and variations
QUESTIONS = [
    "Today sales (dispatch)?",
    "This month sales (dispatch)?",
    "This year sales dispatch?",
    "Today sales order?",
    "This month sales order?",
    "Today SO Nepal?",
    "Today SO export?",
    "Today dispatch total?",
    "Current month sales?",
    "Current FY sales dispatch?",
    "Aaja production kati cha?",
    "Yo mahina production kati cha?",
    "Current FY production?",
    "Yesterday production?",
    "Clinker production current FY?",
    "Aaja attendance kati cha?",
    "Today attendance?",
    "Ghorahi plant attendance?",
    "Kathmandu office attendance?",
    "Clinker stock kati cha?",
    "Stock of PPC cement?",
    "Empty bag stock?",
    "Aaja raw material kati receive bhayo?",
    "Today received Gypsum?",
    "Current FY received Indian Coal?",
    "What information can you provide?",
    "What can you do?",
    "Current_FY sales dispatch Nepal?",
    "Today OPC and PPC sales order?",
]


async def main():
    data_path = Path(__file__).parent / "sample_api_data.json"
    with open(data_path, encoding="utf-8") as f:
        raw = json.load(f)
    sample_rows = _normalize_rows(raw)

    async def mock_fetch(*args, **kwargs):
        return sample_rows

    # Patch in tools so run_sales_force_tool uses sample data (tools imports fetch from client)
    import app.service.tools as tools_mod
    tools_mod.fetch_sales_force_return_data = mock_fetch

    graph = get_compiled_graph()
    results = []

    for i, question in enumerate(QUESTIONS, 1):
        try:
            out = await graph.ainvoke({"question": question})
            reply = (out.get("reply") or "").strip()
            status = "OK" if reply else "NO_DATA"
            preview = (reply[:220] + "…") if len(reply) > 220 else reply
            results.append((i, question, status, preview))
        except Exception as e:
            results.append((i, question, "ERR", str(e)[:200]))

    # Print report
    print("=" * 80)
    print("30 QUESTIONS TEST (sample API data)")
    print("=" * 80)
    for i, q, status, text in results:
        print(f"\n{i:2}. [{status}] {q}")
        print(f"    {text[:250]}" if text else "    (no output)")
    print("\n" + "=" * 80)
    ok = sum(1 for r in results if r[2] == "OK")
    no_data = sum(1 for r in results if r[2] == "NO_DATA")
    err = sum(1 for r in results if r[2] == "ERR")
    print(f"Summary: OK={ok}  NO_DATA={no_data}  ERR={err}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
