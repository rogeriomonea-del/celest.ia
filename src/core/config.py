"""Configuration management for Celes.ia application."""
from __future__ import annotations

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_")
    
    url: str = Field(default="postgresql://celestia_user:password@localhost:5432/celestia_db")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="celestia_db")
    user: str = Field(default="celestia_user")
    password: str = Field(default="password")


class APISettings(BaseSettings):
    """API configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="API_")
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    secret_key: str = Field(default="dev-secret-key")
    debug: bool = Field(default=True)


class LLMSettings(BaseSettings):
    """LLM configuration settings."""
    
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    default_provider: str = Field(default="openai")
    default_model: str = Field(default="gpt-4-turbo-preview")


class TelegramSettings(BaseSettings):
    """Telegram bot configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")
    
    bot_token: Optional[str] = Field(default=None)
    webhook_url: Optional[str] = Field(default=None)


class ScrapingSettings(BaseSettings):
    """Web scraping configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="SCRAPING_")
    
    delay: int = Field(default=2)
    max_retries: int = Field(default=3)
    request_timeout: int = Field(default=30)


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    
    # General settings
    redis_url: str = Field(default="redis://localhost:6379/0")
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/celestia.log")


# Global settings instance
settings = Settings()
