#!/bin/bash

# Script de instalação do Celes.ia Bot
echo "🚀 Instalando Celes.ia Bot..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Cria ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativa ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instala dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite o arquivo .env e adicione seu TELEGRAM_BOT_TOKEN"
echo "2. Execute: source venv/bin/activate"
echo "3. Execute: python start_bot.py"
echo ""
echo "💡 Para obter um token do bot:"
echo "   - Fale com @BotFather no Telegram"
echo "   - Digite /newbot e siga as instruções"
echo "   - Copie o token e cole no arquivo .env"
