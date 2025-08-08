#!/usr/bin/env bash
set -euo pipefail

# ===========================
# === CONFIGURE ME FIRST! ===
# ===========================
# 1) Edit these values before running.
PROJECT_ID="SEU_PROJECT_ID"             # ex: meu-projeto-123
REGION="southamerica-east1"             # São Paulo
SERVICE="celestia-backend"
REPOSITORY="celestia-registry"          # Artifact Registry repo
QUEUE="celestia-queue"                  # Cloud Tasks queue
MIGRATION_JOB="celestia-migrate"        # Cloud Run Job name for Alembic
SA_NAME="celestia-deploy"               # Service Account name (no domain)
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 2) Database URL (temporário para rodar a migração). Recomendo Secret Manager depois.
#    Formato: postgresql+psycopg2://USER:PASS@HOST:5432/DBNAME
DATABASE_URL="postgresql+psycopg2://USER:PASS@HOST:5432/DBNAME"

# 3) (Opcional) Variáveis para Telegram e Anti-captcha (deixe vazio se não for usar agora)
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID=""
ANTICAPTCHA_PROVIDER=""
ANTICAPTCHA_KEY=""

# 4) Credenciais de login (preencha se já tiver, senão pode deixar vazio e configurar depois)
LATAM_USER="49547775855"
LATAM_PASS="8880Cabotcliffsdr!"
AZUL_USER=""
AZUL_PASS=""
SMILES_USER=""
SMILES_PASS=""
CONNECTMILES_USER="rogerio@camelopizzaria.com"
CONNECTMILES_PASS="8880Cabotcliffsdr!"
GOL_USER=""
GOL_PASS=""
LIVELO_USER="rogerio@camelopizzaria.com"
LIVELO_PASS="8880Cabotcliffsdr"

# ===========================
# === DO NOT EDIT BELOW  ===
# ===========================

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud não encontrado. Instale o Google Cloud SDK." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker não encontrado. Instale o Docker Desktop/Engine." >&2
  exit 1
fi

# Ensure we're at repo root (must contain backend/ and infra/cloudrun/cloudrun.yaml)
if [[ ! -d "backend" || ! -f "infra/cloudrun/cloudrun.yaml" ]]; then
  echo "Execute este script na raiz do repositório. backend/ ou infra/cloudrun/cloudrun.yaml não encontrados." >&2
  exit 1
fi

echo ">> Ativando APIs necessárias..."
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com \
  cloudtasks.googleapis.com \
  cloudscheduler.googleapis.com \
  sqladmin.googleapis.com \
  --project "${PROJECT_ID}" >/dev/null

echo ">> Criando Service Account (${SA_EMAIL}) e vinculando papéis (idempotente)..."
gcloud iam service-accounts create "${SA_NAME}" --project "${PROJECT_ID}" >/dev/null 2>&1 || true
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin" >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.admin" >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudtasks.admin" >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.admin" >/dev/null

echo ">> Criando/garantindo Artifact Registry ${REPOSITORY}..."
gcloud artifacts repositories create "${REPOSITORY}" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="Celestia Docker registry" \
  --project "${PROJECT_ID}" >/dev/null 2>&1 || true

echo ">> Fazendo login no Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q

# Build & push image
TAG="$(date +%Y%m%d-%H%M%S)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE}:${TAG}"

echo ">> Build da imagem: ${IMAGE}"
docker build -t "${IMAGE}" -f backend/Dockerfile .
echo ">> Push da imagem..."
docker push "${IMAGE}"

# Expand manifest and set image
echo ">> Expandindo manifest Cloud Run..."
mkdir -p .deploy
sed "s/PROJECT_ID/${PROJECT_ID}/g" infra/cloudrun/cloudrun.yaml > .deploy/cloudrun.expanded.yaml
sed -i.bak "s|celestia-backend:latest|${SERVICE}:${TAG}|g" .deploy/cloudrun.expanded.yaml
rm -f .deploy/cloudrun.expanded.yaml.bak

echo ">> Deploy no Cloud Run (${REGION})..."
gcloud run services replace .deploy/cloudrun.expanded.yaml --region="${REGION}" --project "${PROJECT_ID}"

# Allow unauth (temporário; remova depois se quiser apenas invocador autenticado)
echo ">> Permitindo invocação pública (temporário)..."
gcloud run services add-iam-policy-binding "${SERVICE}" \
  --region="${REGION}" \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project "${PROJECT_ID}" >/dev/null 2>&1 || true

# Get URL and set SERVICE_URL env
SERVICE_URL="$(gcloud run services describe "${SERVICE}" --region="${REGION}" --project "${PROJECT_ID}" --format='value(status.url)')"
echo ">> Serviço publicado em: ${SERVICE_URL}"

echo ">> Atualizando SERVICE_URL como env do serviço..."
gcloud run services update "${SERVICE}" --region="${REGION}" --project "${PROJECT_ID}" \
  --set-env-vars "SERVICE_URL=${SERVICE_URL}" >/dev/null

# Ensure Cloud Tasks queue
echo ">> Criando fila Cloud Tasks (${QUEUE}) (idempotente)..."
gcloud tasks queues create "${QUEUE}" --location="${REGION}" --project "${PROJECT_ID}" >/dev/null 2>&1 || true

# (Re)create Secret Manager entries (idempotente; novas versions)
function upsert_secret() {
  local name="$1"
  local value="$2"
  if [[ -z "${value}" ]]; then
    return 0
  fi
  if ! gcloud secrets describe "${name}" --project "${PROJECT_ID}" >/dev/null 2>&1; then
    printf "%s" "${value}" | gcloud secrets create "${name}" --replication-policy=automatic --project "${PROJECT_ID}" --data-file=- >/dev/null
  else
    printf "%s" "${value}" | gcloud secrets versions add "${name}" --project "${PROJECT_ID}" --data-file=- >/dev/null
  fi
}

echo ">> Gravando secrets no Secret Manager (se valores preenchidos)..."
upsert_secret "database-url" "${DATABASE_URL}"
upsert_secret "telegram-bot-token" "${TELEGRAM_BOT_TOKEN}"
upsert_secret "telegram-chat-id" "${TELEGRAM_CHAT_ID}"
upsert_secret "anticaptcha-provider" "${ANTICAPTCHA_PROVIDER}"
upsert_secret "anticaptcha-key" "${ANTICAPTCHA_KEY}"
upsert_secret "latam_user" "${LATAM_USER}"
upsert_secret "latam_pass" "${LATAM_PASS}"
upsert_secret "azul_user" "${AZUL_USER}"
upsert_secret "azul_pass" "${AZUL_PASS}"
upsert_secret "smiles_user" "${SMILES_USER}"
upsert_secret "smiles_pass" "${SMILES_PASS}"
upsert_secret "connectmiles_user" "${CONNECTMILES_USER}"
upsert_secret "connectmiles_pass" "${CONNECTMILES_PASS}"
upsert_secret "gol_user" "${GOL_USER}"
upsert_secret "gol_pass" "${GOL_PASS}"
upsert_secret "livelo_user" "${LIVELO_USER}"
upsert_secret "livelo_pass" "${LIVELO_PASS}"

echo ">> (Opcional) mapear secrets como envs no serviço Cloud Run?"
echo "   Edite infra/cloudrun/cloudrun.yaml para adicionar mais 'valueFrom.secretKeyRef' conforme necessário, e redeploy."

# Create/Update Cloud Run Job for Alembic migrations
echo ">> Criando/atualizando Cloud Run Job para migrações Alembic..."
# Delete if exists (ignore errors)
gcloud run jobs delete "${MIGRATION_JOB}" --region "${REGION}" --project "${PROJECT_ID}" --quiet >/dev/null 2>&1 || true
gcloud run jobs create "${MIGRATION_JOB}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
  --service-account "${SA_EMAIL}" \
  --command "bash" --args "-lc","alembic upgrade head" >/dev/null

echo ">> Executando migrações (Run Job)..."
gcloud run jobs execute "${MIGRATION_JOB}" --region "${REGION}" --project "${PROJECT_ID}" --wait

# Provision Scheduler (hourly) for three routes
echo ">> Provisionando Cloud Scheduler (jobs horários para 3 rotas)..."
TZ="America/Sao_Paulo"
SA_INVOKER="${SA_EMAIL}"

function create_job() {
  local name="$1"
  local json_body="$2"
  local schedule="$3"
  gcloud scheduler jobs create http "$name" \
    --schedule="$schedule" --time-zone="$TZ" \
    --http-method=POST --uri="${SERVICE_URL}/search/enqueue" \
    --oidc-service-account-email="${SA_INVOKER}" \
    --message-body="$json_body" \
    --location="${REGION}" --project "${PROJECT_ID}" >/dev/null 2>&1 || true
}

create_job "hourly-gru-mco" '{"origin":"GRU","destination":"MCO","departure_date":"2025-09-01"}' "3 * * * *"
create_job "hourly-cgh-sdu" '{"origin":"CGH","destination":"SDU","departure_date":"2025-09-01"}' "13 * * * *"
create_job "hourly-gru-lis" '{"origin":"GRU","destination":"LIS","departure_date":"2025-09-01"}' "23 * * * *"

echo ""
echo "======================================="
echo "Setup concluído com sucesso!"
echo "Service URL: ${SERVICE_URL}"
echo "Fila Cloud Tasks: ${QUEUE}"
echo "Scheduler jobs: hourly-gru-mco, hourly-cgh-sdu, hourly-gru-lis"
echo "Para ajustar secrets adicionais, use: gcloud secrets versions add <nome> --data-file=-"
echo "======================================="
