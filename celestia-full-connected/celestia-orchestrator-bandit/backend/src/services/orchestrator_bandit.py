import time, asyncio
from typing import List, Dict
from sqlalchemy.orm import Session
from db.base import SessionLocal
from services.telemetry import get_http_health, record_run
from services.strategy import decide_mode
from sources.capabilities import Mode
from core.logging import logger

# Import scrapers (placeholders; substituir por implementações reais)
from sources.latam.latam import LatamScraper
from sources.azul.azul import AzulScraper
from sources.smiles.smiles import SmilesScraper
from sources.connectmiles.connectmiles import ConnectmilesScraper
from sources.gol.gol import GolScraper
from sources.livelo.livelo import LiveloScraper

def creds_available(source: str) -> bool:
    import os
    mapping = {
        "latam": ("LATAM_USER","LATAM_PASS"),
        "azul": ("AZUL_USER","AZUL_PASS"),
        "smiles": ("SMILES_USER","SMILES_PASS"),
        "connectmiles": ("CONNECTMILES_USER","CONNECTMILES_PASS"),
        "gol": ("GOL_USER","GOL_PASS"),
        "livelo": ("LIVELO_USER","LIVELO_PASS"),
    }
    if source not in mapping: 
        return True
    u, p = mapping[source]
    return bool(os.getenv(u)) and bool(os.getenv(p))

def build_scraper(source: str):
    # Aqui podemos injetar credenciais no construtor quando necessário
    mapping = {
        "latam": LatamScraper,
        "azul": AzulScraper,
        "smiles": SmilesScraper,
        "connectmiles": ConnectmilesScraper,
        "gol": GolScraper,
        "livelo": LiveloScraper,
    }
    cls = mapping.get(source)
    if not cls:
        raise ValueError(f"Fonte não suportada: {source}")
    return cls()

async def try_http(scraper, origin, destination, date) -> List[Dict]:
    return await scraper.search(origin, destination, date, mode="http")

async def try_selenium(scraper, origin, destination, date) -> List[Dict]:
    # login opcional + search usando fluxo selenium
    await scraper.login()
    return await scraper.search(origin, destination, date, mode="selenium")

async def run_source(source: str, origin: str, destination: str, date: str) -> List[Dict]:
    start = time.time()
    route = f"{origin}-{destination}"
    scraper = build_scraper(source)
    db: Session = SessionLocal()
    try:
        http_health = get_http_health(db)
        order = decide_mode(source, creds_ok=creds_available(source), http_health=http_health)

        for mode in order:
            try:
                if mode == Mode.HTTP:
                    data = await try_http(scraper, origin, destination, date)
                else:
                    data = await try_selenium(scraper, origin, destination, date)
                ok = bool(data)
                latency = int((time.time() - start) * 1000)
                record_run(db, source=source, mode=mode.value, route=route, ok=ok, latency_ms=latency, fail_reason=None if ok else "empty")
                if ok: 
                    return data
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                record_run(db, source=source, mode=mode.value, route=route, ok=False, latency_ms=latency, fail_reason=str(e))
                # self-healing: continua para próximo modo
                continue
        return []
    finally:
        db.close()

async def run_priority_sources(origin: str, destination: str, date: str) -> List[Dict]:
    sources = ["latam", "azul", "smiles", "connectmiles", "gol", "livelo"]
    results = []
    for src in sources:
        out = await run_source(src, origin, destination, date)
        results.extend(out)
    return results
