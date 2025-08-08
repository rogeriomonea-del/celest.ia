#!/usr/bin/env python3
"""Verificador de status do Celes.ia Bot"""

import asyncio
import sys
import os
from pathlib import Path
import json

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv

# Tenta importar bibliotecas opcionais
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

load_dotenv()

def check_file_permissions():
    """Verifica permissões de arquivos."""
    files_to_check = [
        '.env',
        'start_bot.py',
        'requirements.txt'
    ]
    
    print("📁 Verificando arquivos...")
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path} - encontrado")
        else:
            print(f"  ❌ {file_path} - não encontrado")

def check_directories():
    """Verifica se os diretórios necessários existem."""
    dirs_to_check = [
        'src',
        'src/bot',
        'src/api', 
        'src/core',
        'logs',
        'cache'
    ]
    
    print("\n📂 Verificando diretórios...")
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"  ✅ {dir_path}/ - encontrado")
        else:
            print(f"  ❌ {dir_path}/ - não encontrado")

def check_environment_variables():
    """Verifica variáveis de ambiente."""
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Token do bot do Telegram',
    }
    
    optional_vars = {
        'OPENAI_API_KEY': 'Chave da API do OpenAI',
        'DATABASE_URL': 'URL do banco de dados',
        'REDIS_URL': 'URL do Redis',
        'API_PORT': 'Porta da API',
    }
    
    print("\n🔧 Verificando variáveis de ambiente...")
    
    # Variáveis obrigatórias
    print("  📋 Obrigatórias:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Oculta parte do token por segurança
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"    ✅ {var} = {display_value}")
        else:
            print(f"    ❌ {var} - não configurado ({description})")
    
    # Variáveis opcionais
    print("  📋 Opcionais:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"    ✅ {var} - configurado")
        else:
            print(f"    ⚠️  {var} - não configurado ({description})")

def check_python_dependencies():
    """Verifica dependências Python."""
    dependencies = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'python-dotenv',
        'httpx',
        'requests',
        'loguru'
    ]
    
    print("\n🐍 Verificando dependências Python...")
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"  ✅ {dep} - instalado")
        except ImportError:
            print(f"  ❌ {dep} - não instalado")

async def check_telegram_bot():
    """Verifica se o bot do Telegram está funcionando."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("\n🤖 ❌ Token do bot não configurado - pulando teste do Telegram")
        return
    
    print("\n🤖 Testando conexão com Telegram...")
    
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                data = response.json()
        elif REQUESTS_AVAILABLE:
            import requests
            response = requests.get(url, timeout=10)
            data = response.json()
        else:
            print("  ❌ Nenhuma biblioteca HTTP disponível (httpx ou requests)")
            return
        
        if data.get('ok'):
            bot_info = data.get('result', {})
            print(f"  ✅ Bot conectado: @{bot_info.get('username')}")
            print(f"  ℹ️  Nome: {bot_info.get('first_name')}")
            print(f"  ℹ️  ID: {bot_info.get('id')}")
        else:
            print(f"  ❌ Erro da API: {data.get('description')}")
            
    except Exception as e:
        print(f"  ❌ Erro de conexão: {e}")

async def check_api_health():
    """Verifica se a API local está funcionando."""
    api_port = os.getenv('API_PORT', '8000')
    api_host = os.getenv('API_HOST', 'localhost')
    
    print(f"\n🌐 Testando API local ({api_host}:{api_port})...")
    
    url = f"http://{api_host}:{api_port}/health"
    
    try:
        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                if response.status_code == 200:
                    print("  ✅ API respondendo")
                else:
                    print(f"  ⚠️  API retornou status {response.status_code}")
        else:
            print("  ℹ️  httpx não disponível - não é possível testar API")
            
    except Exception as e:
        print(f"  ❌ API não está respondendo: {e}")
        print("  💡 Execute 'python start_bot.py' para iniciar a API")

def print_summary():
    """Imprime resumo e próximos passos."""
    print("\n" + "="*60)
    print("📋 RESUMO E PRÓXIMOS PASSOS")
    print("="*60)
    
    print("\n✅ Se tudo estiver funcionando:")
    print("   python start_bot.py")
    
    print("\n❌ Se houver problemas:")
    print("   1. Instale dependências: ./install.sh")
    print("   2. Configure .env com seu token")
    print("   3. Execute: python start_bot.py")
    
    print("\n🔗 Links úteis:")
    print("   • Obter token: https://t.me/botfather")
    print("   • Documentação: ./BOT_README.md")
    print("   • API docs: http://localhost:8000/docs")

async def main():
    """Função principal."""
    print("🚀 Verificador de Status - Celes.ia Bot")
    print("="*60)
    
    check_file_permissions()
    check_directories()
    check_environment_variables()
    check_python_dependencies()
    await check_telegram_bot()
    await check_api_health()
    
    print_summary()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Verificação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {e}")
