#!/usr/bin/env python3
"""
Script de validação de configuração do Celes.ia.
Verifica se todas as variáveis de ambiente necessárias estão configuradas.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

def check_file_exists(filepath: str) -> bool:
    """Verifica se um arquivo existe."""
    return Path(filepath).exists()

def check_env_file() -> tuple[bool, List[str]]:
    """Verifica arquivo .env."""
    errors = []
    
    if not check_file_exists('.env'):
        errors.append("Arquivo .env não encontrado")
        if check_file_exists('.env.example'):
            errors.append("💡 Copie .env.example para .env e configure as variáveis")
        return False, errors
    
    return True, []

def get_env_value(key: str, default: Any = None) -> Any:
    """Obtém valor de variável de ambiente."""
    value = os.getenv(key, default)
    if value is None:
        return None
    
    # Converte strings especiais
    if isinstance(value, str):
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        elif value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value
    
    return value

def validate_telegram_config() -> tuple[bool, List[str]]:
    """Valida configuração do Telegram."""
    errors = []
    
    bot_token = get_env_value('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        errors.append("TELEGRAM_BOT_TOKEN não configurado")
        errors.append("💡 Obtenha um token em https://t.me/botfather")
    elif not isinstance(bot_token, str) or ':' not in bot_token:
        errors.append("TELEGRAM_BOT_TOKEN tem formato inválido")
    
    return len(errors) == 0, errors

def validate_api_config() -> tuple[bool, List[str]]:
    """Valida configuração da API."""
    errors = []
    
    port = get_env_value('API_PORT', 8000)
    if not isinstance(port, int) or port < 1024 or port > 65535:
        errors.append("API_PORT deve ser um número entre 1024 e 65535")
    
    secret_key = get_env_value('API_SECRET_KEY')
    if secret_key and len(str(secret_key)) < 16:
        errors.append("API_SECRET_KEY deve ter pelo menos 16 caracteres")
    
    return len(errors) == 0, errors

def validate_llm_config() -> tuple[bool, List[str]]:
    """Valida configuração de LLM."""
    errors = []
    warnings = []
    
    openai_key = get_env_value('OPENAI_API_KEY')
    anthropic_key = get_env_value('ANTHROPIC_API_KEY')
    
    if not openai_key and not anthropic_key:
        warnings.append("Nenhuma chave de IA configurada - funcionalidades limitadas")
        warnings.append("💡 Configure OPENAI_API_KEY ou ANTHROPIC_API_KEY")
    
    temperature = get_env_value('LLM_TEMPERATURE', 0.7)
    if not isinstance(temperature, (int, float)) or not 0.0 <= temperature <= 1.0:
        errors.append("LLM_TEMPERATURE deve ser um número entre 0.0 e 1.0")
    
    max_tokens = get_env_value('LLM_MAX_TOKENS', 2000)
    if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 8192:
        errors.append("LLM_MAX_TOKENS deve ser um número entre 1 e 8192")
    
    return len(errors) == 0, errors + warnings

def validate_database_config() -> tuple[bool, List[str]]:
    """Valida configuração do banco de dados."""
    errors = []
    
    db_url = get_env_value('DATABASE_URL')
    if db_url:
        if db_url.startswith('sqlite'):
            # Verifica se o diretório existe
            db_path = db_url.replace('sqlite:///', '')
            db_dir = Path(db_path).parent
            if not db_dir.exists():
                try:
                    db_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Erro ao criar diretório do banco: {e}")
        elif not any(db_url.startswith(prefix) for prefix in ['postgresql://', 'mysql://', 'mariadb://']):
            errors.append("DATABASE_URL deve começar com postgresql://, mysql://, mariadb:// ou sqlite:///")
    
    return len(errors) == 0, errors

def validate_logging_config() -> tuple[bool, List[str]]:
    """Valida configuração de logging."""
    errors = []
    
    log_level = get_env_value('LOG_LEVEL', 'INFO')
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if str(log_level).upper() not in valid_levels:
        errors.append(f"LOG_LEVEL deve ser um de: {valid_levels}")
    
    # Verifica se diretório de logs existe
    log_file = get_env_value('LOG_FILE', 'logs/celestia.log')
    log_dir = Path(log_file).parent
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Erro ao criar diretório de logs: {e}")
    
    return len(errors) == 0, errors

def validate_directories() -> tuple[bool, List[str]]:
    """Valida estrutura de diretórios."""
    errors = []
    
    required_dirs = ['src', 'src/bot', 'src/api', 'src/core']
    optional_dirs = ['logs', 'data', 'cache']
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            errors.append(f"Diretório obrigatório não encontrado: {dir_path}")
    
    for dir_path in optional_dirs:
        if not Path(dir_path).exists():
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Erro ao criar diretório {dir_path}: {e}")
    
    return len(errors) == 0, errors

def print_section(title: str, is_valid: bool, messages: List[str]):
    """Imprime seção de validação."""
    icon = "✅" if is_valid else "❌"
    print(f"\n{icon} {title}")
    
    for msg in messages:
        prefix = "  💡 " if msg.startswith("💡") else "  ⚠️  " if "warning" in msg.lower() else "  • "
        print(f"{prefix}{msg}")

def main():
    """Função principal."""
    print("🔧 Validador de Configuração - Celes.ia")
    print("=" * 60)
    
    if not DOTENV_AVAILABLE:
        print("⚠️  python-dotenv não instalado - usando apenas variáveis do sistema")
    
    overall_valid = True
    
    # Verifica arquivo .env
    env_valid, env_errors = check_env_file()
    print_section("Arquivo .env", env_valid, env_errors)
    overall_valid &= env_valid
    
    # Valida configurações
    validations = [
        ("Configuração Telegram", validate_telegram_config),
        ("Configuração API", validate_api_config),
        ("Configuração LLM/IA", validate_llm_config),
        ("Configuração Banco de Dados", validate_database_config),
        ("Configuração Logging", validate_logging_config),
        ("Estrutura de Diretórios", validate_directories),
    ]
    
    for title, validator in validations:
        is_valid, messages = validator()
        print_section(title, is_valid, messages)
        overall_valid &= is_valid
    
    # Resumo final
    print("\n" + "=" * 60)
    if overall_valid:
        print("🎉 CONFIGURAÇÃO VÁLIDA!")
        print("✅ Todas as verificações passaram")
        print("💫 O projeto está pronto para uso")
    else:
        print("⚠️  CONFIGURAÇÃO COM PROBLEMAS")
        print("❌ Corrija os erros acima antes de prosseguir")
        print("📖 Consulte o arquivo INSTRUCOES_FINAIS.md para ajuda")
    
    print("\n🚀 Para iniciar o bot:")
    print("   python start_bot.py")
    print("\n📖 Para mais informações:")
    print("   cat BOT_README.md")
    
    return 0 if overall_valid else 1

if __name__ == "__main__":
    sys.exit(main())
