from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CODEX_API_KEY = os.getenv("CODEX_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
CELESTIA_API_KEY = os.getenv("CELESTIA_API_KEY")

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

import sys
from pathlib import Path
import glob

# Tenta importar configurações centralizadas
try:
    from config import settings
    # Usa configurações centralizadas se disponível
    model = settings.llm.default_model
    temperature = settings.llm.temperature
except ImportError:
    # Fallback para variáveis de ambiente diretas
    model = os.getenv("LLM_DEFAULT_MODEL", "gpt-4o")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Verifica se a chave foi configurada
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY não configurado!")
    print("💡 Configure no arquivo .env:")
    print("   OPENAI_API_KEY=sua_chave_aqui")
    sys.exit(1)

# Encontra todos os .py do projeto (exceto venvs, __pycache__, etc)
python_files = sorted([
    f for f in glob.glob("**/*.py", recursive=True)
    if not any(x in f for x in ["__pycache__", "venv", ".venv", "site-packages"])
])

# Exibe menu numerado
print("\nEscolha o arquivo para análise:\n")
for i, file in enumerate(python_files):
    print(f"{i+1}. {file}")

# Lê escolha do usuário
try:
    choice = int(input("\nDigite o número do arquivo desejado: "))
    filename = python_files[choice - 1]
except (ValueError, IndexError):
    print("Entrada inválida. Finalizando.")
    exit(1)

# Lê o conteúdo do arquivo selecionado
with open(filename, "r") as f:
    code_to_analyze = f.read()

print(f"\n🔍 Analisando: {filename}\n")

# Envia para o Codex
response = client.chat.completions.create(
    model=model,
    temperature=temperature,
    messages=[
        {"role": "system", "content": "Você é um engenheiro de software experiente especializado em análise e otimização de código Python."},
        {"role": "user", "content": f"Analise, otimize e comente este código Python:\n\nArquivo: {filename}\n\n```python\n{code_to_analyze}\n```"}
    ]
)

# Exibe resultado
print("\n===== RESPOSTA DO CODEX =====\n")
print(response.choices[0].message.content)
