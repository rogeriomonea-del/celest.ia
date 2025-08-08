from typing import List, Dict, Optional
from sources.common.session import HttpSession
from sources.common.normalize import normalize_result
from core.logging import logger

BASE_URL = "https://skyscanner.example"  # Substituir pela URL real

class SkyscannerParser:
    def parse(self, html: str) -> List[Dict]:
        # TODO: implementar com BeautifulSoup/selectolax p/ HTML real
        return []

class SkyscannerScraper:
    def __init__(self, user: Optional[str] = None, password: Optional[str] = None):
        self.user = user
        self.password = password
        self.parser = SkyscannerParser()

    async def login(self) -> None:
        # TODO: fluxo real de login (quando necessário)
        return None

    async def search(self, origin: str, destination: str, date: str, **kwargs) -> List[Dict]:
        params = {"from": origin, "to": destination, "date": date}
        async with HttpSession() as s:
            r = await s.get(BASE_URL, params=params)
            r.raise_for_status()
            items = self.parser.parse(r.text)
            for it in items:
                it.setdefault("source", "skyscanner")
            return items
