#!/usr/bin/env python3
"""
Setup automático do projeto Celes.ia.
Configura automaticamente o arquivo .env e valida a configuração.
"""
import os
import sys
import secrets
from pathlib import Path
from typing import Dict, Any, Optional

def create_secure_key() -> str:
    """Gera uma chave secreta segura."""
    return secrets.token_urlsafe(32)

def get_user_input(prompt: str, default: Optional[str] = None, required: bool = True) -> str:
    """Obtém entrada do usuário com validação."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        
        if required:
            print("❌ Este campo é obrigatório. Tente novamente.")

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Obtém resposta sim/não do usuário."""
    default_text = "S/n" if default else "s/N"
    while True:
        response = input(f"{prompt} ({default_text}): ").strip().lower()
        if not response:
            return default
        if response in ['s', 'sim', 'y', 'yes']:
            return True
        elif response in ['n', 'não', 'nao', 'no']:
            return False
        print("❌ Responda com 's' para sim ou 'n' para não.")

def setup_telegram_config() -> Dict[str, Any]:
    """Configura Telegram bot."""
    print("\n🤖 Configuração do Telegram Bot")
    print("-" * 40)
    
    config = {}
    
    print("Para configurar o bot, você precisa de um token do @BotFather")
    print("💡 Passos:")
    print("   1. Abra o Telegram e procure por @BotFather")
    print("   2. Digite /newbot e siga as instruções")
    print("   3. Copie o token fornecido")
    
    token = get_user_input("\n🔑 Token do bot (formato: 123456789:ABCDEF...)", required=False)
    if token:
        config['TELEGRAM_BOT_TOKEN'] = token
        
        if get_yes_no("🌐 Configurar webhook para produção?", False):
            webhook_url = get_user_input("📡 URL do webhook (https://...)")
            config['TELEGRAM_WEBHOOK_URL'] = webhook_url
    else:
        print("⚠️  Token não configurado - você pode adicionar depois no arquivo .env")
    
    return config

def setup_api_config() -> Dict[str, Any]:
    """Configura API."""
    print("\n🌐 Configuração da API")
    print("-" * 40)
    
    config = {}
    
    host = get_user_input("🏠 Host do servidor", "0.0.0.0", False)
    if host:
        config['API_HOST'] = host
    
    port = get_user_input("🚪 Porta do servidor", "8000", False)
    if port:
        config['API_PORT'] = port
    
    # Gera chave secreta automaticamente
    config['API_SECRET_KEY'] = create_secure_key()
    print("🔐 Chave secreta gerada automaticamente")
    
    debug = get_yes_no("🐛 Modo debug (desenvolvimento)?", True)
    config['API_DEBUG'] = str(debug).lower()
    
    return config

def setup_llm_config() -> Dict[str, Any]:
    """Configura LLM/IA."""
    print("\n🧠 Configuração de IA")
    print("-" * 40)
    
    config = {}
    
    print("Para funcionalidades de IA, configure pelo menos uma chave:")
    
    openai_key = get_user_input("🤖 Chave OpenAI (sk-...)", required=False)
    if openai_key:
        config['OPENAI_API_KEY'] = openai_key
    
    anthropic_key = get_user_input("🧠 Chave Anthropic (sk-ant-...)", required=False)
    if anthropic_key:
        config['ANTHROPIC_API_KEY'] = anthropic_key
    
    if not openai_key and not anthropic_key:
        print("⚠️  Nenhuma chave de IA configurada - funcionalidades limitadas")
    
    # Configurações adicionais
    provider = get_user_input("🔧 Provedor padrão", "openai", False)
    if provider:
        config['LLM_DEFAULT_PROVIDER'] = provider
    
    model = get_user_input("🎯 Modelo padrão", "gpt-4o", False)
    if model:
        config['LLM_DEFAULT_MODEL'] = model
    
    return config

def setup_database_config() -> Dict[str, Any]:
    """Configura banco de dados."""
    print("\n🗄️ Configuração do Banco de Dados")
    print("-" * 40)
    
    config = {}
    
    use_sqlite = get_yes_no("📁 Usar SQLite (recomendado para desenvolvimento)?", True)
    
    if use_sqlite:
        db_path = get_user_input("💾 Caminho do banco SQLite", "sqlite:///./data/celestia.db", False)
        if db_path:
            config['DATABASE_URL'] = db_path
    else:
        print("🐘 Configuração PostgreSQL:")
        host = get_user_input("🏠 Host", "localhost", False)
        port = get_user_input("🚪 Porta", "5432", False)
        name = get_user_input("📊 Nome do banco", "celestia_db", False)
        user = get_user_input("👤 Usuário", "celestia_user", False)
        password = get_user_input("🔒 Senha", required=False)
        
        if all([host, port, name, user]):
            url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
            config['DATABASE_URL'] = url
    
    return config

def setup_additional_config() -> Dict[str, Any]:
    """Configura opções adicionais."""
    print("\n⚙️ Configurações Adicionais")
    print("-" * 40)
    
    config = {}
    
    if get_yes_no("📊 Configurar logging detalhado?", False):
        log_level = get_user_input("📈 Nível de log", "INFO", False)
        if log_level:
            config['LOG_LEVEL'] = log_level.upper()
    
    if get_yes_no("🕷️ Configurar scraping?", False):
        delay = get_user_input("⏱️ Delay entre requisições (segundos)", "2", False)
        if delay:
            config['SCRAPING_DELAY'] = delay
    
    return config

def write_env_file(config: Dict[str, Any]) -> bool:
    """Escreve arquivo .env."""
    try:
        env_path = Path('.env')
        
        # Backup se já existe
        if env_path.exists():
            backup_path = Path('.env.backup')
            env_path.rename(backup_path)
            print(f"💾 Backup do .env existente salvo como {backup_path}")
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Configuração gerada automaticamente pelo setup do Celes.ia\n")
            f.write(f"# Gerado em: {os.popen('date').read().strip()}\n")
            f.write("# Para reconfigurar, execute: python setup.py\n\n")
            
            # Organiza por seções
            sections = {
                "TELEGRAM": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_WEBHOOK_URL"],
                "API": ["API_HOST", "API_PORT", "API_SECRET_KEY", "API_DEBUG"],
                "LLM": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LLM_DEFAULT_PROVIDER", "LLM_DEFAULT_MODEL"],
                "DATABASE": ["DATABASE_URL"],
                "LOGGING": ["LOG_LEVEL"],
                "SCRAPING": ["SCRAPING_DELAY"],
            }
            
            for section, keys in sections.items():
                section_configs = {k: v for k, v in config.items() if k in keys}
                if section_configs:
                    f.write(f"# {section}\n")
                    for key, value in section_configs.items():
                        f.write(f"{key}={value}\n")
                    f.write("\n")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao escrever .env: {e}")
        return False

def create_directories():
    """Cria diretórios necessários."""
    dirs = ['logs', 'data', 'cache']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("📁 Diretórios criados: " + ", ".join(dirs))

def main():
    """Função principal."""
    print("🚀 Setup Automático - Celes.ia Bot")
    print("=" * 60)
    print("Este assistente irá configurar seu projeto automaticamente.")
    print("Você pode pular qualquer seção pressionando Enter.\n")
    
    if not get_yes_no("🎯 Iniciar configuração?", True):
        print("👋 Setup cancelado pelo usuário.")
        return 0
    
    # Coleta configurações
    all_config = {}
    
    all_config.update(setup_telegram_config())
    all_config.update(setup_api_config())
    all_config.update(setup_llm_config())
    all_config.update(setup_database_config())
    all_config.update(setup_additional_config())
    
    # Cria diretórios
    print("\n📁 Criando estrutura de diretórios...")
    create_directories()
    
    # Escreve arquivo .env
    print("\n💾 Salvando configurações...")
    if write_env_file(all_config):
        print("✅ Arquivo .env criado com sucesso!")
    else:
        print("❌ Erro ao criar arquivo .env")
        return 1
    
    # Resumo
    print("\n📋 Resumo da Configuração:")
    print("-" * 40)
    for key, value in all_config.items():
        # Oculta valores sensíveis
        if 'KEY' in key or 'TOKEN' in key or 'PASSWORD' in key:
            display_value = value[:10] + "..." if len(str(value)) > 10 else "***"
        else:
            display_value = value
        print(f"  {key}: {display_value}")
    
    print("\n🎉 Configuração concluída!")
    print("🔧 Execute 'python validate_config.py' para validar")
    print("🚀 Execute 'python start_bot.py' para iniciar o bot")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante o setup: {e}")
        sys.exit(1)
