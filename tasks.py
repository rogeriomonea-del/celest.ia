#!/usr/bin/env python3
"""
Task runner para o projeto Celes.ia.
Facilita execução de tarefas comuns de desenvolvimento.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command: str, description: str = None) -> bool:
    """Executa comando e retorna sucesso."""
    if description:
        print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return False

def task_install():
    """Instala dependências."""
    print("📦 Instalando dependências...")
    
    # Verifica se está em venv
    if not os.getenv('VIRTUAL_ENV'):
        print("⚠️  Recomendado usar ambiente virtual:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate     # Windows")
        if not input("\nContinuar mesmo assim? (s/N): ").lower().startswith('s'):
            return False
    
    return run_command("pip install -r requirements.txt", "Instalando pacotes Python")

def task_setup():
    """Executa setup interativo."""
    print("⚙️ Executando setup interativo...")
    return run_command("python setup.py", "Configurando projeto")

def task_validate():
    """Valida configuração."""
    print("✅ Validando configuração...")
    return run_command("python validate_config.py", "Verificando configurações")

def task_start():
    """Inicia o bot."""
    print("🚀 Iniciando bot...")
    return run_command("python start_bot.py", "Iniciando Celes.ia Bot")

def task_check():
    """Verifica status do sistema."""
    print("📊 Verificando status...")
    return run_command("python check_status.py", "Verificando sistema")

def task_test():
    """Executa testes."""
    print("🧪 Executando testes...")
    if not Path("pytest.ini").exists():
        # Cria configuração básica de testes
        with open("pytest.ini", "w") as f:
            f.write("""[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
""")
    return run_command("python -m pytest tests/", "Executando testes")

def task_format():
    """Formata código."""
    print("🎨 Formatando código...")
    success = True
    success &= run_command("black .", "Formatando com Black")
    success &= run_command("flake8 --max-line-length=100 --ignore=E203,W503 .", "Verificando com Flake8")
    return success

def task_clean():
    """Limpa arquivos temporários."""
    print("🧹 Limpando arquivos temporários...")
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache",
        "**/.coverage",
        "**/htmlcov",
        "**/.mypy_cache",
        "**/logs/*.log*",
        "**/cache/*",
    ]
    
    for pattern in patterns:
        run_command(f"find . -path './{pattern}' -delete 2>/dev/null || true", f"Removendo {pattern}")
    
    return True

def task_dev():
    """Modo desenvolvimento com auto-reload."""
    print("🔧 Iniciando em modo desenvolvimento...")
    os.environ['API_DEBUG'] = 'true'
    return run_command("uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000", "Servidor dev")

def task_webhook():
    """Configura webhook."""
    print("🌐 Configurador de webhook...")
    return run_command("python setup_webhook.py", "Configurando webhook")

def task_deps():
    """Atualiza dependências."""
    print("⬆️ Atualizando dependências...")
    success = True
    success &= run_command("pip list --outdated", "Verificando atualizações")
    if input("\nAtualizar pacotes? (s/N): ").lower().startswith('s'):
        success &= run_command("pip install -U pip", "Atualizando pip")
        success &= run_command("pip install -U -r requirements.txt", "Atualizando pacotes")
    return success

def task_help():
    """Mostra ajuda."""
    tasks = {
        'install': 'Instala dependências',
        'setup': 'Configuração interativa do projeto',
        'validate': 'Valida configuração atual',
        'start': 'Inicia o bot do Telegram',
        'check': 'Verifica status do sistema',
        'test': 'Executa testes',
        'format': 'Formata código (black + flake8)',
        'clean': 'Remove arquivos temporários',
        'dev': 'Inicia servidor em modo desenvolvimento',
        'webhook': 'Configura webhook do Telegram',
        'deps': 'Atualiza dependências',
        'help': 'Mostra esta ajuda',
    }
    
    print("🛠️ Tarefas disponíveis:")
    print("-" * 40)
    for task, description in tasks.items():
        print(f"  {task:<12} - {description}")
    
    print("\n💡 Uso: python tasks.py <tarefa>")
    print("📖 Exemplo: python tasks.py setup")
    return True

def main():
    """Função principal."""
    if len(sys.argv) != 2:
        task_help()
        return 1
    
    task_name = sys.argv[1]
    task_function = f"task_{task_name}"
    
    if hasattr(sys.modules[__name__], task_function):
        print(f"🎯 Executando tarefa: {task_name}")
        print("=" * 50)
        
        success = getattr(sys.modules[__name__], task_function)()
        
        print("=" * 50)
        if success:
            print(f"✅ Tarefa '{task_name}' concluída com sucesso!")
            return 0
        else:
            print(f"❌ Tarefa '{task_name}' falhou!")
            return 1
    else:
        print(f"❌ Tarefa '{task_name}' não encontrada!")
        task_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
