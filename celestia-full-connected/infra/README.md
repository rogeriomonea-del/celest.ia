# Celest.ia — Tudo conectado (HTTP + Selenium, AI scaffolding, testes)

## O que está pronto
- **Scrapers**: HTTP (httpx + parsers bs4/selectolax) e **Selenium headless** com Chromium/Chromedriver no container.
- **Pipeline**: enqueue via Cloud Tasks → handler no Cloud Run → persiste no Postgres.
- **Orquestração**: regras e sumarização (LLM plugável).
- **Self-healing**: retries progressivos, fallback de parsers e parâmetros alternativos.
- **Self-improvement (base)**: ganchos para registrar sucesso/falha e priorizar caminhos vencedores.
- **ML (base)**: pronto para ingestão; adicione modelos em `src/ml/` e job de treino via Scheduler.
- **Testes reais (pytest)**: parsers e pipeline com DB (sqlite in-memory por padrão).
- **CI/CD**: workflows para rodar testes e deploy em Cloud Run (SP).

## Como rodar localmente
```bash
pip install -r backend/requirements.txt
export DATABASE_URL=sqlite+pysqlite:///:memory:
python - <<'PY'
from backend.src.api.main import app
print("App OK", app)
PY
pytest
```

## Deploy
- Configure `GCP_PROJECT_ID` e `GCP_SA_KEY` nos Secrets do GitHub.
- Commit na `main` dispara build/test/deploy.
- Crie a fila `celestia-queue` (workflow já tenta criar).
- Atualize o `SERVICE_URL` depois do primeiro deploy (ou ajuste no CD).

## Próximos passos sugeridos
- Substituir URLs e seletores placeholders por **endpoints reais** (LATAM, Azul, Smiles, metabuscadores).
- Escrever **parsers específicos por site** em `src/services/parsers_<site>.py` e selecionar por `source`.
- Implementar **notificação Telegram** pós-processamento.
- Adicionar **feature store** simples (tabela com features agregadas) e job de treino (Cloud Scheduler).

