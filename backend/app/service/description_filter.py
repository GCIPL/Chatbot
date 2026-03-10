"""Filter API rows by question-derived time/product. Uses description registry."""
import json
from pathlib import Path
from typing import Any

from app.models import NormalizedRow


def _load_registry(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {"timeHints": [], "productHints": []}
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    return {
        "timeHints": data.get("timeHints", []),
        "productHints": data.get("productHints", []),
    }


def _question_lower(question: str) -> str:
    return question.strip().lower()


def _match_time(question: str, registry: dict[str, Any]) -> str | None:
    """Return descriptionContains for time, or None if no match (then pass all)."""
    q = _question_lower(question)
    for entry in registry.get("timeHints", []):
        hints = entry.get("hints", [])
        if any(h in q for h in hints):
            return entry.get("descriptionContains")
    return None


def _match_product(question: str, registry: dict[str, Any]) -> str | None:
    """Return descriptionContains for product, or None for all."""
    q = _question_lower(question)
    for entry in registry.get("productHints", []):
        hints = entry.get("hints", [])
        if any(h in q for h in hints):
            return entry.get("descriptionContains")
    return None


def filter_rows_by_question(
    rows: list[NormalizedRow],
    question: str,
    registry_path: Path | None = None,
) -> list[NormalizedRow]:
    """
    Keep only rows whose description matches the question (time + product).
    Uses description registry; if no registry, returns all rows.
    Also contains a special fallback for production questions where the user
    asks for "today" but only "Yesterday ..." production rows exist.
    """
    if registry_path is None:
        base_filtered = rows
    else:
        registry = _load_registry(registry_path)
        time_contains = _match_time(question, registry)
        product_contains = _match_product(question, registry)

        def matches(row: NormalizedRow) -> bool:
            d = row.description
            if time_contains and time_contains not in d:
                return False
            if product_contains and product_contains not in d:
                return False
            return True

        base_filtered = [r for r in rows if matches(r)]

    # If we have matches, return them.
    if base_filtered:
        return base_filtered

    # Fallback: for production-style questions that mention "today"/"aaja"/"aj",
    # but there is no explicit Today data, use Yesterday production rows.
    q = _question_lower(question)
    is_today_like = any(h in q for h in ("today", "aaja", "aj"))
    # Heuristics for production questions (clinker, cement, coal, raw meal, utpadan, etc.)
    is_production_like = any(
        h in q
        for h in (
            "production",
            "utpadan",
            "clinker",
            "cement",
            "fine coal",
            "raw meal",
            "raw mix",
        )
    )
    if not (is_today_like and is_production_like):
        return base_filtered

    # At this point we assume rows are already limited to production metric_type
    # by the caller (run_sales_force_tool). Select Yesterday rows only.
    fallback_rows: list[NormalizedRow] = [
        r for r in rows if r.description.startswith("Yesterday")
    ]
    return fallback_rows
