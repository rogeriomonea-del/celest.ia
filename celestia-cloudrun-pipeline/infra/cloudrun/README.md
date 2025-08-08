# Celest.ia — Pipeline pronto no Cloud Run (SP) com Cloud Tasks

Arquitetura de execução sem servidor de filas (sem Redis):
- **Cloud Run** (FastAPI) — recebe webhooks, expõe API e processa tarefas via handlers HTTP
- **Cloud Tasks** — enfileira chamadas HTTP para o handler `/tasks/handler/search`
- **Cloud Scheduler** (opcional) — dispara buscas recorrentes
- **Cloud SQL Postgres** — persistência
- (Opcional) **Secret Manager** — gerenciar chaves

## Passos

### 1) Service Account e permissões
Crie `celestia-deploy` e adicione:
- roles/run.admin
- roles/artifactregistry.admin
- roles/iam.serviceAccountUser
- roles/cloudtasks.admin
- (opcional) roles/secretmanager.admin
- (opcional) roles/cloudsql.admin

Exporte a chave JSON e adicione como secret do GitHub: `GCP_SA_KEY`.

### 2) Secrets do GitHub
- `GCP_PROJECT_ID`
- `GCP_SA_KEY`
- (opcionais) `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`

### 3) Banco (Cloud SQL) e DATABASE_URL
Provisionar Postgres em `southamerica-east1`. Configure `DATABASE_URL` via Secret Manager (ou direto no manifest para testes).

### 4) Primeiro deploy
Commit na `main` → workflow publica a imagem no Artifact Registry e aplica o manifest. O job imprime a **URL** do serviço Cloud Run e seta `SERVICE_URL` automaticamente.

### 5) Fila (Cloud Tasks)
O workflow garante a fila `celestia-queue`. A API `/search/enqueue` cria tasks que chamam o handler `/tasks/handler/search`.

### 6) Agendamentos (Cloud Scheduler) — opcional
Exemplo (busca diária GRU-MCO às 08:00 SP):
```bash
REGION=southamerica-east1
PROJECT_ID=SEU_PROJECT_ID
SERVICE_URL=$(gcloud run services describe celestia-backend --region=$REGION --format='value(status.url)')

gcloud scheduler jobs create http daily-search-gru-mco   --schedule="0 8 * * *" --time-zone="America/Sao_Paulo"   --http-method=POST   --uri="$SERVICE_URL/search/enqueue"   --oidc-service-account-email="celestia-deploy@$PROJECT_ID.iam.gserviceaccount.com"   --message-body='{"origin":"GRU","destination":"MCO","departure_date":"2025-09-01"}'   --location=$REGION
```

### 7) Webhook do Telegram
Após o serviço estar no ar:
```bash
SERVICE_URL=$(gcloud run services describe celestia-backend --region=southamerica-east1 --format='value(status.url)')
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook"   -d "url=$SERVICE_URL/bot/webhook"   -d "secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

### 8) Teste rápido
- `GET $SERVICE_URL/health`
- `POST $SERVICE_URL/search/enqueue` com JSON `{"origin":"GRU","destination":"MCO","departure_date":"2025-09-01"}`
- Ou, no Telegram: `/search GRU MCO 2025-09-01`

Resultados são gravados na tabela `flight_prices`.
