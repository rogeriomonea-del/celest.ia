from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    env: str = Field(default="production", alias="ENV")
    port: int = Field(default=8080, alias="PORT")
    gcp_project_id: str | None = Field(default=None, alias="GCP_PROJECT_ID")
    gcp_location: str = Field(default="southamerica-east1", alias="GCP_LOCATION")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    codex_api_key: str | None = Field(default=None, alias="CODEX_API_KEY")
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")
    celestia_api_key: str | None = Field(default=None, alias="CELESTIA_API_KEY")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str | None = Field(default=None, alias="TELEGRAM_WEBHOOK_SECRET")

    database_url: str = Field(default="sqlite+pysqlite:///:memory:", alias="DATABASE_URL")

    service_url: str | None = Field(default=None, alias="SERVICE_URL")  # Cloud Run URL (opcional p/ enqueue)

    class Config:
        case_sensitive = False

settings = Settings()
