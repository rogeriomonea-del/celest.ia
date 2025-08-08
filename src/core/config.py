"""Configuration management for Celes.ia application."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_")
    
    url: str = Field(default="sqlite:///./data/celestia.db")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="celestia_db")
    user: str = Field(default="celestia_user")
    password: str = Field(default="")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    
    @property
    def connection_url(self) -> str:
        """Retorna URL de conexão construída."""
        if self.url and not self.url.startswith('sqlite'):
            return self.url
        elif self.url.startswith('sqlite'):
            # Garante que o diretório existe
            db_path = Path(self.url.replace('sqlite:///', ''))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return self.url
        else:
            # Constrói URL a partir dos componentes
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="API_")
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    secret_key: str = Field(default="dev-secret-change-in-production")
    debug: bool = Field(default=True)
    cors_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 16:
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS."""
        return [origin.strip() for origin in self.cors_origins.split(',')]


class LLMSettings(BaseSettings):
    """LLM configuration settings."""
    
    model_config = SettingsConfigDict(env_prefix="LLM_")
    
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_provider: str = Field(default="openai")
    default_model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperatura deve estar entre 0.0 e 1.0')
        return v


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
