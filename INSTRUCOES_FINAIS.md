# 🎯 INSTRUÇÕES FINAIS - Como configurar seu bot

## � CONFIGURAÇÃO AUTOMÁTICA (RECOMENDADO)

### 1️⃣ **Setup Automático**
```bash
# Instala dependências
python tasks.py install

# Configuração interativa
python tasks.py setup

# Valida configuração
python tasks.py validate

# Inicia o bot
python tasks.py start
```

## 📝 CONFIGURAÇÃO MANUAL

### 1️⃣ **OBTENHA SEU TOKEN DO TELEGRAM**
1. Abra o Telegram
2. Procure por `@BotFather`
3. Digite `/newbot`
4. Escolha um nome para seu bot (ex: "Meu Celes.ia Bot")
5. Escolha um username (ex: "meu_celestia_bot")
6. **COPIE O TOKEN** que será exibido (formato: `1234567890:ABCDEF...`)

### 2️⃣ **CONFIGURE O ARQUIVO .env**
```bash
# Opção 1: Setup automático
python setup.py

# Opção 2: Manual - copie o exemplo
cp .env.example .env
# Edite o .env e adicione seu token
```

### 3️⃣ **INSTALE AS DEPENDÊNCIAS**
```bash
# Usando task runner
python tasks.py install

# Ou manualmente:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4️⃣ **TESTE A CONFIGURAÇÃO**
```bash
# Validação completa
python tasks.py validate

# Ou verificação de status
python tasks.py check
```

### 5️⃣ **INICIE O BOT**
```bash
# Produção
python tasks.py start

# Desenvolvimento (com auto-reload)
python tasks.py dev
```

---

## 🛠️ TASK RUNNER - Comandos Disponíveis

O projeto inclui um task runner (`tasks.py`) para facilitar operações comuns:

```bash
python tasks.py <comando>
```

### 📋 **Comandos Principais:**
- `install` - Instala dependências
- `setup` - Configuração interativa do projeto
- `validate` - Valida configuração atual
- `start` - Inicia o bot do Telegram
- `check` - Verifica status do sistema
- `dev` - Inicia servidor em modo desenvolvimento
- `webhook` - Configura webhook do Telegram

### 🧹 **Comandos de Desenvolvimento:**
- `test` - Executa testes
- `format` - Formata código (black + flake8)
- `clean` - Remove arquivos temporários
- `deps` - Atualiza dependências
- `help` - Mostra todos os comandos

---

## 🛠️ Arquivos criados:

### 📋 **Configuração:**
- ✅ `.env.example` - Exemplo completo de configuração
- ✅ `config.py` - Sistema centralizado de configurações
- ✅ `setup.py` - Setup automático interativo
- ✅ `validate_config.py` - Validador de configuração
- ✅ `tasks.py` - Task runner para automação

### 🚀 **Scripts de execução:**
- ✅ `start_bot.py` - Inicializador principal do bot
- ✅ `install.sh` - Script de instalação automática
- ✅ `check_status.py` - Verificador de status e configuração
- ✅ `setup_webhook.py` - Configurador de webhook (para produção)

### 📂 **Pastas criadas:**
- ✅ `logs/` - Arquivos de log do sistema
- ✅ `cache/` - Cache temporário
- ✅ `data/` - Dados da aplicação

### 📖 **Documentação:**
- ✅ `BOT_README.md` - Documentação completa do bot
- ✅ `INSTRUCOES_FINAIS.md` - Este arquivo

---

## � NOVA FUNCIONALIDADE: Configuração por Variáveis de Ambiente

O projeto agora suporta configuração completa via arquivo `.env`:

### 🤖 **Telegram Bot**
```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/webhook
```

### 🧠 **Inteligência Artificial**
```env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_DEFAULT_PROVIDER=openai
LLM_DEFAULT_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
```

### 🌐 **API e Servidor**
```env
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=chave-super-secreta
API_DEBUG=true
```

### 🗄️ **Banco de Dados**
```env
DATABASE_URL=sqlite:///./data/celestia.db
# ou
DATABASE_URL=postgresql://user:pass@host:port/db
```

### 📊 **Logging**
```env
LOG_LEVEL=INFO
LOG_FILE=logs/celestia.log
LOG_FORMAT=detailed
```

### 🔐 **Segurança**
```env
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8
RATE_LIMIT_PER_MINUTE=60
FORCE_HTTPS=true
```

---

## 🆘 Resolução de problemas:

### ❌ "Configuração inválida"
```bash
# Valide a configuração
python tasks.py validate

# Reconfigure se necessário
python tasks.py setup
```

### ❌ "Módulo não encontrado" 
```bash
# Reinstale dependências
python tasks.py install

# Ou force reinstalação
pip install -r requirements.txt --force-reinstall
```

### ❌ "Bot não responde"
```bash
# Verifique status
python tasks.py check

# Verifique logs
tail -f logs/celestia.log
```

### ❌ "Erro de permissão"
```bash
# Torne scripts executáveis
chmod +x install.sh tasks.py setup.py
```

---

## 🚀 Fluxo de trabalho recomendado:

### 🆕 **Primeira configuração:**
```bash
# 1. Setup completo
python tasks.py setup

# 2. Validação
python tasks.py validate

# 3. Teste
python tasks.py dev
```

### 🔄 **Desenvolvimento:**
```bash
# Inicia modo desenvolvimento
python tasks.py dev

# Em outro terminal - executa testes
python tasks.py test

# Formata código
python tasks.py format
```

### 🌐 **Produção:**
```bash
# Configuração de produção
python tasks.py webhook

# Inicia bot
python tasks.py start
```

---

## 💡 Dicas avançadas:

### 🔧 **Múltiplos ambientes:**
```bash
# Desenvolvimento
cp .env.example .env.dev
python setup.py  # configure para dev

# Produção  
cp .env.example .env.prod
python setup.py  # configure para prod

# Use específico
python -c "from config import load_settings; s=load_settings('.env.prod')"
```

### 📊 **Monitoramento:**
```bash
# Logs em tempo real
tail -f logs/celestia.log

# Status do sistema
python tasks.py check

# Métricas
python -c "from config import settings; print(settings.get_summary())"
```

### 🧪 **Testes:**
```bash
# Todos os testes
python tasks.py test

# Testes específicos
python -m pytest tests/test_bot.py -v

# Coverage
python -m pytest --cov=src tests/
```

---

## 📞 Precisa de ajuda?

1. **Primeira verificação:** `python tasks.py validate`
2. **Status do sistema:** `python tasks.py check`
3. **Logs detalhados:** `tail -f logs/celestia.log`
4. **Documentação:** `cat BOT_README.md`
5. **Reconfiguração:** `python tasks.py setup`

**🎉 AGORA O PROJETO ESTÁ TOTALMENTE CONFIGURADO COM SUPORTE A VARIÁVEIS DE AMBIENTE!**

```bash
# Configuração rápida
python tasks.py setup

# Validação
python tasks.py validate

# Execução
python tasks.py start
```
