from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://cashflow:cashflow@localhost:5432/cashflow_pilot"

    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    default_currency: str = "CHF"

    ai_provider: str = "claude"
    anthropic_api_key: str | None = None

    google_client_id: str | None = None
    google_client_secret: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
