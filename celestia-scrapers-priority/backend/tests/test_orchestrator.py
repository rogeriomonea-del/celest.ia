import asyncio
from sources.pipeline_orchestrator import run_priority_pipeline

def test_orchestrator_runs():
    # Usa placeholders; deve retornar lista (possivelmente vazia) sem exceptions
    out = asyncio.run(run_priority_pipeline("GRU", "MCO", "2025-09-01"))
    assert isinstance(out, list)
