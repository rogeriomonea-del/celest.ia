# Scrapers Prioritários (GRU → MCO)

Fontes: **LATAM Pass, Azul, Smiles, Skyscanner/Google Flights (pré-filtro), Azul Pelo Mundo, Award Hacker, ConnectMiles (Copa), Livelo, GOL**.

## Onde implementar seletores reais
- `backend/src/sources/<fonte>/<fonte>.py` — coloque URLs reais, params e parseadores.
- Logins via Selenium: `backend/src/sources/common/selenium_login.py`.
- Sessões HTTP resilientes: `backend/src/sources/common/session.py`.

## Pipeline de execução priorizada
- `backend/src/sources/pipeline_orchestrator.py` — orquestra a ordem: pre-filtro → programas.
- Ajuste semáforo/concurrency conforme limite de cada site.

## Contratos e normalização
- `backend/src/sources/contracts.py` — Scraper/Parser.
- `backend/src/sources/common/normalize.py` — formato canônico de saída.

## Testes
- `pytest -q` roda validações de contrato e orquestrador (placeholders). Adicione fixtures HTML reais (sem credenciais) para regression tests dos parsers.

## Próximo commit (feito por mim, após você confirmar URLs/seletores):
- Conectar **URLs reais** (sem expor credenciais) e parsers específicos por site.
- Adicionar **fixtures** de HTML estático para Smiles/Azul/LATAM/Skyscanner.
- Testes de integração com coverage de parsing > 90%.
