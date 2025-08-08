import asyncio
from typing import List, Dict
from core.logging import logger
from sources.prefilter import prefilter_routes
from sources.latam.latam import LatamScraper
from sources.azul.azul import AzulScraper
from sources.smiles.smiles import SmilesScraper
from sources.connectmiles.connectmiles import ConnectmilesScraper
from sources.livelo.livelo import LiveloScraper
from sources.gol.gol import GolScraper

async def run_priority_pipeline(origin: str, destination: str, date: str) -> List[Dict]:
    # 1) Prefiltro
    _ = await prefilter_routes(origin, destination, date)
    # 2) Prioridade de programas (ajuste fino depois)
    scrapers = [
        LatamScraper(),
        AzulScraper(),
        SmilesScraper(),
        ConnectmilesScraper(),
        LiveloScraper(),
        GolScraper(),
    ]
    # Executa em paralelo com limites para evitar bloqueios
    sem = asyncio.Semaphore(3)
    async def wrapped(scr):
        async with sem:
            try:
                return await scr.search(origin, destination, date)
            except Exception as e:
                logger.warning(f"Erro em {scr.__class__.__name__}: {e}")
                return []

    results_nested = await asyncio.gather(*[wrapped(s) for s in scrapers])
    results = [item for sub in results_nested for item in sub]
    # TODO: dedup/merge por menor preço
    return results
