import asyncio
from services.orchestrator_extended import run_priority_sources_extended

def test_orchestrator_extended_smoke():
    out = asyncio.run(run_priority_sources_extended("GRU","MCO","2025-09-01"))
    assert isinstance(out, list)
