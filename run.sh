#!/bin/bash

# Diretório do projeto
cd "$(dirname "$0")"

# Ativa o ambiente virtual
if [ ! -f ".venv/bin/activate" ]; then
  echo "❌ Ambiente virtual não encontrado. Crie com: python -m venv .venv"
  exit 1
fi
source .venv/bin/activate

# Verifica se o dotenv está instalado
if ! python -c "import dotenv" &> /dev/null; then
  echo "🛠 Instalando dependências necessárias..."
  pip install -r requirements.txt
fi

# Carrega o .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️ Arquivo .env não encontrado. Crie um baseado no .env.example."
  exit 1
fi

# Verifica se todas as variáveis críticas estão presentes
MISSING_VARS=()
for VAR in OPENAI_API_KEY CODEX_API_KEY GEMINI_API_KEY GITHUB_TOKEN CELESTIA_API_KEY; do
  if [ -z "${!VAR}" ]; then
    MISSING_VARS+=($VAR)
  fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
  echo "❌ As seguintes variáveis não estão definidas no .env:"
  for VAR in "${MISSING_VARS[@]}"; do echo " - $VAR"; done
  exit 1
fi

# Executa o script desejado (padrão: codex_runner.py)
SCRIPT=${1:-codex_runner.py}
echo "🚀 Executando $SCRIPT com ambiente ativado e variáveis carregadas..."
python "$SCRIPT"
