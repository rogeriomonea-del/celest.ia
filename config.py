"""
Configuração centralizada usando variáveis de ambiente.
Este módulo carrega e valida todas as configurações do projeto.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Optional, List, Union
from pydantic import Field, validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    """Configurações do Telegram Bot."""
    
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")
    
    bot_token: Optional[str] = Field(default=None, description="Token do bot do Telegram")
    webhook_url: Optional[str] = Field(default=None, description="URL do webhook")
    
    @validator('bot_token')
    def validate_bot_token(cls, v):
        if v and not v.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
            raise ValueError('Token do Telegram deve começar com dígito')
        return v


class APISettings(BaseSettings):
    """Configurações da API."""
    
    model_config = SettingsConfigDict(env_prefix="API_")
    
    host: str = Field(default="0.0.0.0", description="Host do servidor")
    port: int = Field(default=8000, description="Porta do servidor")
    secret_key: str = Field(default="", description="Chave secreta")
    debug: bool = Field(default=True, description="Modo debug")
    cors_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000", description="URLs CORS permitidas")
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v:
            # Gera uma chave segura se não fornecida
            return secrets.token_urlsafe(32)
        if len(v) < 16:
            raise ValueError('Chave secreta deve ter pelo menos 16 caracteres')
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de origens CORS."""
        return [origin.strip() for origin in self.cors_origins.split(',')]


class LLMSettings(BaseSettings):
    """Configurações de LLM/IA."""
    
    model_config = SettingsConfigDict(env_prefix="LLM_")
    
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_provider: str = Field(default="openai", description="Provedor padrão")
    default_model: str = Field(default="gpt-4o", description="Modelo padrão")
    temperature: float = Field(default=0.7, description="Temperatura")
    max_tokens: int = Field(default=2000, description="Máximo de tokens")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperatura deve estar entre 0.0 e 1.0')
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 1 or v > 8192:
            raise ValueError('max_tokens deve estar entre 1 e 8192')
        return v


class DatabaseSettings(BaseSettings):
    """Configurações do banco de dados."""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_")
    
    url: str = Field(default="sqlite:///./data/celestia.db", description="URL do banco")
    host: str = Field(default="localhost", description="Host do banco")
    port: int = Field(default=5432, description="Porta do banco")
    name: str = Field(default="celestia_db", description="Nome do banco")
    user: str = Field(default="celestia_user", description="Usuário do banco")
    password: str = Field(default="", description="Senha do banco")
    pool_size: int = Field(default=10, description="Tamanho do pool")
    max_overflow: int = Field(default=20, description="Overflow máximo")
    
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


class CacheSettings(BaseSettings):
    """Configurações de cache."""
    
    model_config = SettingsConfigDict(env_prefix="CACHE_")
    
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    ttl: int = Field(default=3600, description="TTL padrão em segundos")
    max_size: int = Field(default=100, description="Tamanho máximo em MB")
    
    @validator('ttl')
    def validate_ttl(cls, v):
        if v < 1:
            raise ValueError('TTL deve ser positivo')
        return v


class ScrapingSettings(BaseSettings):
    """Configurações de scraping."""
    
    model_config = SettingsConfigDict(env_prefix="SCRAPING_")
    
    delay: int = Field(default=2, description="Delay entre requisições")
    max_retries: int = Field(default=3, description="Máximo de tentativas")
    request_timeout: int = Field(default=30, description="Timeout das requisições")
    user_agent: str = Field(default="Mozilla/5.0 (compatible; CelesiaBot/2.0)", description="User-Agent")
    proxy_url: Optional[str] = Field(default=None, description="URL do proxy")


class LoggingSettings(BaseSettings):
    """Configurações de logging."""
    
    model_config = SettingsConfigDict(env_prefix="LOG_")
    
    level: str = Field(default="INFO", description="Nível de log")
    file: str = Field(default="logs/celestia.log", description="Arquivo de log")
    error_file: str = Field(default="logs/errors.log", description="Arquivo de erros")
    rotation_size: int = Field(default=10, description="Tamanho para rotação (MB)")
    retention_days: int = Field(default=30, description="Dias de retenção")
    to_console: bool = Field(default=True, description="Log no console")
    format: str = Field(default="detailed", description="Formato do log")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Nível deve ser um de: {valid_levels}')
        return v.upper()
    
    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['simple', 'detailed', 'json']
        if v not in valid_formats:
            raise ValueError(f'Formato deve ser um de: {valid_formats}')
        return v


class SecuritySettings(BaseSettings):
    """Configurações de segurança."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    allowed_ips: str = Field(default="", description="IPs permitidos")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit por minuto")
    session_timeout: int = Field(default=3600, description="Timeout da sessão")
    force_https: bool = Field(default=False, description="Forçar HTTPS")
    
    @property
    def allowed_ips_list(self) -> List[str]:
        """Retorna lista de IPs permitidos."""
        if not self.allowed_ips:
            return []
        return [ip.strip() for ip in self.allowed_ips.split(',')]


class NotificationSettings(BaseSettings):
    """Configurações de notificação."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from: str = Field(default="noreply@celestia.bot", env="SMTP_FROM")
    webhook_url: Optional[str] = Field(default=None, env="WEBHOOK_URL")


class RegionalSettings(BaseSettings):
    """Configurações regionais."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    timezone: str = Field(default="America/Sao_Paulo", env="TIMEZONE")
    default_language: str = Field(default="pt-BR", env="DEFAULT_LANGUAGE")
    default_currency: str = Field(default="BRL", env="DEFAULT_CURRENCY")


class AirlineSettings(BaseSettings):
    """Configurações de integrações com companhias aéreas."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    latam_api_key: Optional[str] = Field(default=None, env="LATAM_API_KEY")
    azul_api_key: Optional[str] = Field(default=None, env="AZUL_API_KEY")
    gol_api_key: Optional[str] = Field(default=None, env="GOL_API_KEY")
    amadeus_api_key: Optional[str] = Field(default=None, env="AMADEUS_API_KEY")
    amadeus_api_secret: Optional[str] = Field(default=None, env="AMADEUS_API_SECRET")
    skyscanner_api_key: Optional[str] = Field(default=None, env="SKYSCANNER_API_KEY")


class DevelopmentSettings(BaseSettings):
    """Configurações de desenvolvimento."""
    
    model_config = SettingsConfigDict(env_prefix="")
    
    dev_mode: bool = Field(default=True, env="DEV_MODE")
    test_data_seed: int = Field(default=12345, env="TEST_DATA_SEED")
    test_base_url: str = Field(default="http://localhost:8000", env="TEST_BASE_URL")
    test_database_url: str = Field(default="sqlite:///./data/test_celestia.db", env="TEST_DATABASE_URL")


class Settings(BaseSettings):
    """Configurações principais da aplicação."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True
    )
    
    # Sub-configurações
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    api: APISettings = Field(default_factory=APISettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    regional: RegionalSettings = Field(default_factory=RegionalSettings)
    airlines: AirlineSettings = Field(default_factory=AirlineSettings)
    development: DevelopmentSettings = Field(default_factory=DevelopmentSettings)
    
    def __init__(self, **kwargs):
        """Inicializa configurações e garante que diretórios existam."""
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Garante que diretórios necessários existam."""
        directories = [
            Path(self.logging.file).parent,
            Path(self.logging.error_file).parent,
            Path("data"),
            Path("cache"),
            Path("logs")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return not self.api.debug and not self.development.dev_mode
    
    def validate_required_for_production(self) -> List[str]:
        """Valida configurações obrigatórias para produção."""
        errors = []
        
        if self.is_production():
            if not self.telegram.bot_token:
                errors.append("TELEGRAM_BOT_TOKEN é obrigatório em produção")
            
            if self.api.secret_key == "dev-secret-change-in-production":
                errors.append("API_SECRET_KEY deve ser alterado em produção")
            
            if not self.security.force_https:
                errors.append("FORCE_HTTPS deve ser true em produção")
        
        return errors
    
    def get_summary(self) -> dict:
        """Retorna resumo das configurações (sem dados sensíveis)."""
        return {
            "telegram": {
                "bot_configured": bool(self.telegram.bot_token),
                "webhook_configured": bool(self.telegram.webhook_url),
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
                "cors_origins": len(self.api.cors_origins_list),
            },
            "llm": {
                "openai_configured": bool(self.llm.openai_api_key),
                "anthropic_configured": bool(self.llm.anthropic_api_key),
                "provider": self.llm.default_provider,
                "model": self.llm.default_model,
            },
            "database": {
                "type": "sqlite" if "sqlite" in self.database.url else "postgresql",
                "url_configured": bool(self.database.url),
            },
            "environment": {
                "is_production": self.is_production(),
                "dev_mode": self.development.dev_mode,
                "log_level": self.logging.level,
            }
        }


# Instância global das configurações
settings = Settings()


def load_settings(env_file: Optional[str] = None) -> Settings:
    """
    Carrega configurações de um arquivo específico.
    
    Args:
        env_file: Caminho para arquivo .env específico
        
    Returns:
        Instância de Settings configurada
    """
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()


def validate_configuration() -> tuple[bool, List[str]]:
    """
    Valida configuração atual.
    
    Returns:
        Tupla (is_valid, errors)
    """
    errors = []
    
    try:
        # Tenta carregar configurações
        config = Settings()
        
        # Validações específicas
        if config.is_production():
            prod_errors = config.validate_required_for_production()
            errors.extend(prod_errors)
        
        # Verifica token do Telegram se fornecido
        if config.telegram.bot_token and not config.telegram.bot_token.count(':') == 1:
            errors.append("Formato do TELEGRAM_BOT_TOKEN inválido")
        
        # Verifica configurações de IA
        if not config.llm.openai_api_key and not config.llm.anthropic_api_key:
            errors.append("Pelo menos uma chave de API de IA deve ser configurada (OpenAI ou Anthropic)")
        
    except Exception as e:
        errors.append(f"Erro ao carregar configurações: {str(e)}")
    
    return len(errors) == 0, errors


if __name__ == "__main__":
    """Script para testar configurações."""
    print("🔧 Testando configurações do Celes.ia...")
    
    is_valid, errors = validate_configuration()
    
    if is_valid:
        print("✅ Configurações válidas!")
        print("\n📊 Resumo:")
        summary = settings.get_summary()
        for section, data in summary.items():
            print(f"  {section}: {data}")
    else:
        print("❌ Erros encontrados:")
        for error in errors:
            print(f"  • {error}")
    
    print(f"\n🌍 Ambiente: {'Produção' if settings.is_production() else 'Desenvolvimento'}")
