"""Application config from env and config files."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM — set LLM_PROVIDER=openai or gemini when both keys are set; else we prefer Gemini if its key is set
    llm_provider: str = ""  # "openai" | "gemini" | "" (auto: gemini if key set, else openai)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_api_base: str | None = None
    openai_api_version: str | None = None
    openai_deployment: str | None = None

    # Emp portal
    emp_portal_base_url: str = "https://emp-portal.ghorahicement.com"
    sales_force_abc: str = "105"
    # ChatBothLink dashboard grid: returnData?ABC=109 → Name + Web_Excel_Address
    sales_force_abc_chatbot_links: str = "109"

    # App
    assistant_env: str = "development"
    log_level: str = "INFO"

    # Paths (for description registry)
    project_root: Path = Path(__file__).resolve().parent.parent
    config_dir: Path = project_root / ".." / "config"

    def description_registry_path(self) -> Path:
        p = self.project_root.parent / "config" / "description-registry.example.json"
        if not p.exists():
            p = self.project_root / "config" / "description-registry.example.json"
        return p


settings = Settings()
