import asyncio
from typing import List, Dict
from sources.skyscanner.skyscanner import SkyscannerScraper
from sources.googleflights.googleflights import GoogleflightsScraper

async def prefilter_routes(origin: str, destination: str, date: str) -> List[Dict]:
    # Chama metabuscadores para guiar ordem de scraping (mais barato primeiro)
    s1 = SkyscannerScraper()
    s2 = GoogleflightsScraper()
    r1, r2 = await asyncio.gather(s1.search(origin, destination, date), s2.search(origin, destination, date))
    return sorted((r1 + r2), key=lambda x: x.get("price", 1e12))[:10]
