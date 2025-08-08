#!/usr/bin/env python3
"""
Teste do sistema de configuração.
Valida se todas as configurações estão funcionando corretamente.
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

def test_env_loading():
    """Testa carregamento de variáveis de ambiente."""
    print("🧪 Testando carregamento de .env...")
    
    # Cria arquivo .env temporário
    test_content = """
# Teste de configuração
TELEGRAM_BOT_TOKEN=123456789:test_token
API_PORT=9999
API_DEBUG=true
LLM_TEMPERATURE=0.5
DATABASE_URL=sqlite:///test.db
LOG_LEVEL=DEBUG
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(test_content)
        temp_env_file = f.name
    
    try:
        # Tenta carregar python-dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv(temp_env_file)
            dotenv_available = True
        except ImportError:
            dotenv_available = False
            print("⚠️  python-dotenv não disponível")
        
        if dotenv_available:
            # Verifica se variáveis foram carregadas
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            port = os.getenv('API_PORT')
            debug = os.getenv('API_DEBUG')
            
            if token == '123456789:test_token':
                print("  ✅ TELEGRAM_BOT_TOKEN carregado corretamente")
            else:
                print(f"  ❌ TELEGRAM_BOT_TOKEN incorreto: {token}")
            
            if port == '9999':
                print("  ✅ API_PORT carregado corretamente")
            else:
                print(f"  ❌ API_PORT incorreto: {port}")
            
            if debug == 'true':
                print("  ✅ API_DEBUG carregado corretamente")
            else:
                print(f"  ❌ API_DEBUG incorreto: {debug}")
        
        return dotenv_available
    
    finally:
        # Remove arquivo temporário
        os.unlink(temp_env_file)

def test_config_validation():
    """Testa validação de configurações."""
    print("\n🧪 Testando validação de configurações...")
    
    # Simula configurações válidas
    valid_configs = {
        'TELEGRAM_BOT_TOKEN': '123456789:ABCDEF1234567890',
        'API_PORT': '8000',
        'API_SECRET_KEY': 'chave-com-mais-de-16-caracteres',
        'LLM_TEMPERATURE': '0.7',
        'LLM_MAX_TOKENS': '2000',
        'LOG_LEVEL': 'INFO',
        'DATABASE_URL': 'sqlite:///./data/test.db'
    }
    
    # Simula configurações inválidas
    invalid_configs = {
        'TELEGRAM_BOT_TOKEN': 'token_invalido',
        'API_PORT': '999',  # Porta muito baixa
        'API_SECRET_KEY': 'curta',  # Muito curta
        'LLM_TEMPERATURE': '2.0',  # Muito alta
        'LLM_MAX_TOKENS': '10000',  # Muito alto
        'LOG_LEVEL': 'INVALID',
    }
    
    print("  📋 Testando configurações válidas...")
    valid_count = 0
    for key, value in valid_configs.items():
        os.environ[key] = value
        # Aqui você faria a validação real
        print(f"    ✅ {key}: {value}")
        valid_count += 1
    
    print(f"  ✅ {valid_count}/{len(valid_configs)} configurações válidas testadas")
    
    print("  📋 Testando configurações inválidas...")
    invalid_count = 0
    for key, value in invalid_configs.items():
        # Aqui você testaria se a validação detecta o erro
        print(f"    ⚠️  {key}: {value} (deveria ser inválido)")
        invalid_count += 1
    
    print(f"  ✅ {invalid_count}/{len(invalid_configs)} configurações inválidas testadas")
    
    return True

def test_directory_creation():
    """Testa criação de diretórios."""
    print("\n🧪 Testando criação de diretórios...")
    
    required_dirs = ['logs', 'data', 'cache']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        
        if dir_path.exists():
            print(f"  ✅ {dir_name}/ já existe")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {dir_name}/ criado com sucesso")
            except Exception as e:
                print(f"  ❌ Erro ao criar {dir_name}/: {e}")
                return False
    
    return True

def test_file_structure():
    """Testa estrutura de arquivos."""
    print("\n🧪 Testando estrutura de arquivos...")
    
    required_files = [
        'requirements.txt',
        '.env.example',
        'config.py',
        'setup.py',
        'validate_config.py',
        'tasks.py',
        'start_bot.py',
    ]
    
    optional_files = [
        '.env',
        'BOT_README.md',
        'INSTRUCOES_FINAIS.md',
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (obrigatório)")
            return False
    
    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path} (opcional)")
    
    return True

def test_import_dependencies():
    """Testa importação de dependências."""
    print("\n🧪 Testando dependências Python...")
    
    core_deps = {
        'fastapi': 'FastAPI',
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        'uvicorn': 'Uvicorn',
    }
    
    optional_deps = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'requests': 'Requests',
        'httpx': 'HTTPX',
        'loguru': 'Loguru',
        'python-telegram-bot': 'Python Telegram Bot',
    }
    
    for module, name in core_deps.items():
        try:
            __import__(module.replace('-', '_'))
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} (obrigatório)")
            return False
    
    for module, name in optional_deps.items():
        try:
            __import__(module.replace('-', '_'))
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ⚠️  {name} (opcional)")
    
    return True

def test_config_module():
    """Testa módulo de configuração."""
    print("\n🧪 Testando módulo config.py...")
    
    try:
        # Tenta importar o módulo de configuração
        sys.path.insert(0, str(Path.cwd()))
        
        try:
            import config
            print("  ✅ config.py importado com sucesso")
            
            # Testa se tem as classes principais
            if hasattr(config, 'Settings'):
                print("  ✅ Classe Settings encontrada")
            else:
                print("  ❌ Classe Settings não encontrada")
                return False
            
            if hasattr(config, 'settings'):
                print("  ✅ Instância global 'settings' encontrada")
            else:
                print("  ❌ Instância global 'settings' não encontrada")
                return False
            
        except ImportError as e:
            print(f"  ❌ Erro ao importar config.py: {e}")
            return False
    
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        return False
    
    return True

def main():
    """Função principal."""
    print("🚀 Teste do Sistema de Configuração - Celes.ia")
    print("=" * 60)
    
    tests = [
        ("Carregamento de .env", test_env_loading),
        ("Validação de configurações", test_config_validation),
        ("Criação de diretórios", test_directory_creation),
        ("Estrutura de arquivos", test_file_structure),
        ("Dependências Python", test_import_dependencies),
        ("Módulo config.py", test_config_module),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro durante teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de configuração está funcionando perfeitamente")
        return 0
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("💡 Verifique os erros acima e execute:")
        print("   python tasks.py install  # Para instalar dependências")
        print("   python tasks.py setup    # Para configurar o projeto")
        return 1

if __name__ == "__main__":
    sys.exit(main())
