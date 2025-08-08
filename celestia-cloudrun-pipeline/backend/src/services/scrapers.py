from core.logging import logger
from datetime import datetime

# Scraper placeholder (substituir por scraping real ou integrações)
async def fetch_prices(origin: str, destination: str, date: str) -> list[dict]:
    logger.info(f"Fetching prices for {origin}-{destination} {date}")
    # Simulação: três fontes
    base = [
        {"route": f"{origin}-{destination}", "date": date, "price": 2450.0, "source": "Skyscanner"},
        {"route": f"{origin}-{destination}", "date": date, "price": 2330.0, "source": "LATAM Pass"},
        {"route": f"{origin}-{destination}", "date": date, "price": 2575.0, "source": "Azul"},
    ]
    return base
