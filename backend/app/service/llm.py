"""LLM factory: Gemini (if GEMINI_API_KEY set) or OpenAI (if OPENAI_API_KEY set)."""
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import settings


def get_llm() -> BaseChatModel | None:
    """
    Return the configured chat model. Use LLM_PROVIDER if set (openai|gemini), else prefer Gemini then OpenAI.
    """
    use_openai = (settings.llm_provider or "").strip().lower() == "openai"
    use_gemini = (settings.llm_provider or "").strip().lower() == "gemini"
    if not use_openai and (use_gemini or (settings.gemini_api_key and settings.gemini_api_key.strip())):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=0,
                google_api_key=settings.gemini_api_key.strip(),
            )
        except ImportError:
            pass
    if settings.openai_api_key and settings.openai_api_key.strip():
        from langchain_openai import ChatOpenAI
        kwargs = dict(
            model=settings.openai_model,
            temperature=0,
            api_key=settings.openai_api_key.strip(),
        )
        if settings.openai_api_base:
            kwargs["base_url"] = settings.openai_api_base
            if settings.openai_api_version:
                kwargs["api_version"] = settings.openai_api_version
        return ChatOpenAI(**kwargs)
    return None
