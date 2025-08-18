# Celestia – Fix Bundle (08/Ago)

Este pacote corrige:
- `pytest.ini` na raiz (limita os testes a `backend/tests` e define `PYTHONPATH=backend/src`)
- `backend/requirements.txt` com pins compatíveis (inclui `google-cloud-tasks==2.19.3`)
- Workflow **Deploy Celestia Backend (Cloud Run - SP)** (`.github/workflows/deploy-cloudrun.yml`)
- `infra/cloudrun/cloudrun.yaml` (manifest base – a imagem é substituída pelo workflow)
- `backend/Dockerfile` com Chromium e Chromedriver
- `tools/run_all.py` para rodar as 3 rotas canônicas

## Como aplicar
1. Extraia o zip na **raiz do repositório** (vai sobrescrever/mesclar estes arquivos).
2. Faça commit destes arquivos na sua branch e `push`.
3. No GitHub, crie os Secrets:
   - **Obrigatórios**: `GCP_PROJECT_ID`, `GCP_SA_KEY`, `DATABASE_URL`
   - **Opcionais**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, e credenciais das cias (`LATAM_*`, `AZUL_*`, `SMILES_*`, etc.)
4. Vá em **Actions → Deploy Celestia Backend (Cloud Run - SP)** → **Run workflow**.
5. Ao final, veja a `Service URL` impressa no job e confirme que os 3 agendamentos foram criados.

> Depois da primeira execução, baixe os logs em `logs/cdp/` e me envie para eu fixar os endpoints definitivos por fonte.
