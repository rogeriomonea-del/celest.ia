# Celest.ia — Deploy no Google Cloud Run (São Paulo)

Siga estes passos em ordem. Sem pressa, mas com precisão.

## 1) Service Account e permissões
(iguais ao pacote anterior) — crie `celestia-deploy` e adicione `roles/run.admin`, `roles/artifactregistry.admin`, `roles/iam.serviceAccountUser`.
Se for usar Cloud SQL/Secrets, adicione `roles/cloudsql.admin` e `roles/secretmanager.admin`.

Exporte a chave JSON e salve como secret `GCP_SA_KEY` no GitHub.

## 2) Secrets no GitHub (Actions)
- `GCP_PROJECT_ID`
- `GCP_SA_KEY` (JSON do SA)
- (opcionais) `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`

## 3) Banco (Cloud SQL) e Redis (MemoryStore)
Provisionar na região `southamerica-east1` e criar `DATABASE_URL` e `REDIS_URL`.
Para início, você pode usar IP público (Authorized Networks). Ideal: VPC Serverless Access.

## 4) Estrutura do repositório esperada
```
backend/
  Dockerfile
  requirements.txt
  src/
    api/main.py
    core/*
    db/*
infra/cloudrun/cloudrun.yaml
.github/workflows/cd-backend-cloudrun.yml
docker-compose.yml (dev)
backend/alembic.ini
backend/migrations/env.py
```

## 5) Primeiro deploy
- Faça commit na `main`. O workflow vai buildar a imagem, publicar no Artifact Registry e aplicar o manifest.
- A saída do job mostra a **URL do Cloud Run**.

## 6) Webhook do Telegram
Após o serviço estar no ar, configure:
```
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook"   -d "url=https://<URL>/bot/webhook"   -d "secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

## 7) Teste de saúde
Abra `GET https://<URL>/health` — deve retornar `{"status":"ok","env":"production"}`.
