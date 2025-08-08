import asyncio
from typing import List, Dict
from core.logging import logger
from services.orchestrator_bandit import run_source

async def run_priority_sources_extended(origin: str, destination: str, date: str) -> List[Dict]:
    sources = ["latam","azul","smiles","connectmiles","copa","livelo","gol","azulpelomundo","awardhacker"]
    results = []
    for src in sources:
        out = await run_source(src, origin, destination, date)
        results.extend(out)
    return results
