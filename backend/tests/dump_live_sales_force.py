#!/usr/bin/env python3
"""
Dump live Sales Force returnData rows for inspection.
Uses real emp-portal API via fetch_sales_force_return_data.

Run from backend/:
  python -m tests.dump_live_sales_force
"""
import asyncio
from typing import Iterable

from app.internal_api.client import fetch_sales_force_return_data


def _print_rows(title: str, rows: Iterable):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    for r in rows:
        print(f"{r.description!r} | {r.metric_type!r} | {r.quantity}")


async def main():
    rows = await fetch_sales_force_return_data()

    # Quick overall stats
    print(f"Total rows: {len(rows)}")

    today_dispatch = [
        r
        for r in rows
        if r.metric_type
        and "sales dispatch" in r.metric_type.lower()
        and r.description.lower().strip().startswith("today")
    ]
    today_so = [
        r
        for r in rows
        if r.metric_type
        and ("so qnty" in r.metric_type.lower() or "sales order qnty" in r.metric_type.lower())
        and r.description.lower().strip().startswith("today")
    ]

    _print_rows("Today Sales Dispatch rows", today_dispatch)
    _print_rows("Today Sales Order rows", today_so)

    print("\nComputed totals:")
    print("  Today Sales Dispatch total:", sum(r.quantity for r in today_dispatch))
    print("  Today Sales Order total:", sum(r.quantity for r in today_so))


if __name__ == "__main__":
    asyncio.run(main())

