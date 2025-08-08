import asyncio
from services.orchestrator_bandit import run_priority_sources

def test_bandit_orchestrator_smoke():
    # Deve rodar sem exceptions e retornar lista (placeholders podem retornar [])
    out = asyncio.run(run_priority_sources("GRU","MCO","2025-09-01"))
    assert isinstance(out, list)
