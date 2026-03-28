"""Pydantic models for API and graph state."""
from typing import Any

from pydantic import BaseModel, Field


# --- HTTP API ---


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    reply_for_tts: str | None = None
    sources: list[str] = Field(default_factory=list)


class ChatErrorResponse(BaseModel):
    error: str
    message: str


class QuickLinkItem(BaseModel):
    name: str
    url: str


class QuickLinksResponse(BaseModel):
    """Portal shortcuts from Sales Force returnData (ChatBothLink / ABC=109)."""

    links: list[QuickLinkItem] = Field(default_factory=list)
    error: str | None = None


# --- Intent / entities (graph state) ---


class ExtractedEntities(BaseModel):
    time_scope: str | None = None  # today, this month, this year
    product: str | None = None    # OPC, PPC, NP, Exp, or None for all
    intent: str = "sales_summary"  # sales_order, dispatch, production, summary, unsupported


# --- Tool result (description + quantity only; no value) ---


class NormalizedRow(BaseModel):
    description: str
    quantity: float
    metric_type: str | None = None


class ToolResult(BaseModel):
    tool_name: str
    success: bool = True
    rows: list[NormalizedRow] = Field(default_factory=list)
    error: str | None = None


# --- LangGraph state ---


class AssistantState(BaseModel):
    """State passed through the LangGraph. All fields optional for partial updates."""

    question: str = ""
    intent_result: ExtractedEntities | None = None
    tool_results: list[ToolResult] = Field(default_factory=list)
    reply: str = ""
    reply_for_tts: str | None = None
    sources: list[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"

    def to_graph_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_graph_dict(cls, d: dict[str, Any]) -> "AssistantState":
        return cls.model_validate(d)
