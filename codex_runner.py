import os
from openai import OpenAI
from dotenv import load_dotenv
import glob

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Você é um engenheiro de software experiente."},
        {"role": "user", "content": f"Analise, otimize e comente este código Python:\n\n{code_to_analyze}"}
    ]
)

# Exibe resultado
print("\n===== RESPOSTA DO CODEX =====\n")
print(response.choices[0].message.content)
