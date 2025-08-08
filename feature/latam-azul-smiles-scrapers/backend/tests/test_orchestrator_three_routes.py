import asyncio
from services.orchestrator_bandit import run_priority_sources

ROUTES = [
    ("GRU","MCO","2025-09-01"),
    ("CGH","SDU","2025-09-01"),
    ("GRU","LIS","2025-09-01"),
]

def test_orchestrator_three_routes():
    for o,d,dt in ROUTES:
        out = asyncio.run(run_priority_sources(o,d,dt))
        assert isinstance(out, list)
