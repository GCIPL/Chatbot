"""Intent and entity extraction. Uses LLM (Gemini or OpenAI) with structured output."""
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.models import ExtractedEntities
from app.prompts import INTENT_SYSTEM
from app.service.llm import get_llm


def _parse_entities_from_llm(text: str) -> ExtractedEntities:
    """Parse LLM output into ExtractedEntities. Fallback to summary if parse fails."""
    try:
        # Try to find JSON in the response
        text = text.strip()
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        data = json.loads(text)
        return ExtractedEntities(
            time_scope=data.get("time_scope"),
            product=data.get("product"),
            intent=data.get("intent", "sales_summary"),
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        return ExtractedEntities(intent="sales_summary")


async def extract_intent_and_entities(question: str) -> ExtractedEntities:
    """
    Call LLM (Gemini or OpenAI) to extract time_scope, product, intent.
    Requires GEMINI_API_KEY or OPENAI_API_KEY in settings.
    """
    llm = get_llm()
    if llm is None:
        return ExtractedEntities(intent="sales_summary")

    messages = [
        SystemMessage(content=INTENT_SYSTEM),
        HumanMessage(content=question),
    ]
    try:
        response = await llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        return _parse_entities_from_llm(content)
    except Exception:
        return ExtractedEntities(intent="sales_summary")
