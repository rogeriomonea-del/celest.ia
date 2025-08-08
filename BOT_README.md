# 🤖 Celes.ia Telegram Bot

Bot inteligente do Telegram para busca de voos e análise de preços de passagens aéreas.

## 🚀 Instalação Rápida

### 1. Clone e configure
```bash
git clone [seu-repo]
cd Celest.ia-v2-Alpha
```

### 2. Execute o instalador
```bash
./install.sh
```

### 3. Configure o token
1. Fale com [@BotFather](https://t.me/botfather) no Telegram
2. Digite `/newbot` e siga as instruções
3. Copie o token fornecido
4. Edite o arquivo `.env` e cole o token:
```env
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
```

### 4. Inicie o bot
```bash
source venv/bin/activate
python start_bot.py
```

## 📋 Comandos do Bot

### Comandos Básicos
- `/start` - Inicializar o bot
- `/help` - Mostrar ajuda
- `/search origem destino data` - Buscar voos
- `/trends destino` - Ver tendências de preços
- `/miles` - Verificar saldo de milhas
- `/settings` - Configurações do usuário

### Linguagem Natural
O bot entende frases naturais:
- "Quero viajar de São Paulo para Rio no dia 15"
- "Preços para Paris em dezembro"
- "Como estão os preços para Miami?"

## 🛠️ Configuração Avançada

### Variáveis de Ambiente (.env)
```env
# Obrigatório
TELEGRAM_BOT_TOKEN=seu_token_aqui

# Opcional - Para funcionalidades de IA
OPENAI_API_KEY=sua_chave_openai

# Configuração da API
API_HOST=0.0.0.0
API_PORT=8000

# Banco de dados (opcional)
DATABASE_URL=postgresql://user:pass@localhost:5432/celestia

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0
```

### Estrutura do Projeto
```
Celest.ia-v2-Alpha/
├── .env                    # Configurações
├── start_bot.py           # Inicializador principal
├── install.sh             # Script de instalação
├── requirements.txt       # Dependências Python
├── src/
│   ├── bot/              # Lógica do bot
│   │   ├── handlers.py   # Manipuladores de mensagens
│   │   └── commands.py   # Comandos do bot
│   ├── api/              # API FastAPI
│   │   ├── main.py       # Aplicação principal
│   │   └── routes/       # Rotas da API
│   └── core/             # Núcleo da aplicação
│       ├── config.py     # Configurações
│       └── orchestrator.py # Orquestrador principal
├── logs/                 # Arquivos de log
└── cache/               # Cache de dados
```

## 🔧 Desenvolvimento

### Executar em modo debug
```bash
export API_DEBUG=true
python start_bot.py
```

### Executar testes
```bash
pip install pytest
pytest tests/
```

### Verificar logs
```bash
tail -f logs/celestia_bot.log
```

## 🌐 Webhook (Produção)

Para uso em produção, configure o webhook:

```bash
curl -X POST "https://api.telegram.org/bot{BOT_TOKEN}/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://seu-dominio.com/api/v1/telegram/webhook"}'
```

## 📊 Funcionalidades

### ✅ Implementado
- [x] Bot básico do Telegram
- [x] Comandos de busca de voos
- [x] Análise de tendências
- [x] Linguagem natural
- [x] API REST completa
- [x] Sistema de logging
- [x] Configuração por variáveis de ambiente

### 🔄 Em desenvolvimento
- [ ] Integração com companhias aéreas
- [ ] Verificação de milhas
- [ ] Alertas de preços
- [ ] Reservas diretas
- [ ] Análise preditiva com IA

## 🐛 Resolução de Problemas

### Bot não responde
1. Verifique se o token está correto no `.env`
2. Verifique os logs: `tail -f logs/celestia_bot.log`
3. Teste a API: `http://localhost:8000/docs`

### Erro de instalação
1. Verifique se Python 3.8+ está instalado
2. Execute `pip install --upgrade pip`
3. Instale dependências manualmente: `pip install -r requirements.txt`

### Problemas de conexão
1. Verifique sua conexão com a internet
2. Verifique se as portas não estão bloqueadas
3. Para produção, configure HTTPS

## 📞 Suporte

- 📧 Email: [seu-email]
- 🐛 Issues: [GitHub Issues]
- 📖 Documentação: [Wiki do projeto]

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

---

**Desenvolvido com ❤️ para facilitar suas viagens!** ✈️
