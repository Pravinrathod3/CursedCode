from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_env: str = "development"
    app_name: str = "Debug Dojo API"
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:5173"

    # Supabase — service role key; never expose to frontend
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # LLM provider
    llm_provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    xai_api_key: str = ""
    xai_model: str = ""

    # Code runner (Judge0 REST API)
    runner_base_url: str = "https://judge0-ce.p.rapidapi.com"
    runner_api_key: str = ""
    runner_timeout_seconds: int = 15
    max_code_bytes: int = 20_000

    # LangSmith (optional)
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "debug-dojo"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
