#!/usr/bin/env bash
set -euo pipefail

REGION="southamerica-east1"
PROJECT_ID="${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
SERVICE_URL="$(gcloud run services describe celestia-backend --region=$REGION --format='value(status.url)')"
SA_EMAIL="celestia-deploy@${PROJECT_ID}.iam.gserviceaccount.com"
TZ="America/Sao_Paulo"

create_job () {
  local name="$1"; shift
  local body="$1"; shift
  local schedule="$1"; shift
  gcloud scheduler jobs create http "$name"     --schedule="$schedule" --time-zone="$TZ"     --http-method=POST --uri="$SERVICE_URL/search/enqueue"     --oidc-service-account-email="$SA_EMAIL"     --message-body="$body"     --location="$REGION" || echo "exists: $name"
}

create_job "hourly-gru-mco" '{"origin":"GRU","destination":"MCO","departure_date":"2025-09-01"}' "3 * * * *"
create_job "hourly-cgh-sdu" '{"origin":"CGH","destination":"SDU","departure_date":"2025-09-01"}' "13 * * * *"
create_job "hourly-gru-lis" '{"origin":"GRU","destination":"LIS","departure_date":"2025-09-01"}' "23 * * * *"

echo "Scheduler jobs created/verified."
