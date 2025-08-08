# Orquestrador com decisão dinâmica (HTTP vs Selenium) + Telemetria

Inclui:
- `sources/capabilities.py` — priors por fonte
- `services/strategy.py` — decisão dinâmica com heurísticas
- `db/models_runs.py` — tabela `runs` para telemetria
- `migrations/versions/*_add_runs.py` — migração Alembic
- `services/telemetry.py` — gravação e agregação de métricas
- `services/orchestrator_bandit.py` — tenta modos por fonte com escada de fallback
- `backend/tests/test_bandit_orchestrator.py` — teste de fumaça

Próximo passo: executar migração Alembic e começar a registrar execuções reais.
