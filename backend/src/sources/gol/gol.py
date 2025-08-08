from typing import List, Dict
from services.selenium_cdp import make_driver_cdp, wait_css, extract_json_endpoints, get_cookies
from services.http_client_ex import make_client
from sources.common.normalize import normalize_result
from core.logging import logger
import os, json

HOST_HINTS = ["voegol.com.br", "gol.com"]

class GolScraper:
    def __init__(self):
        self.user = os.getenv("GOL_USER", "")
        self.password = os.getenv("GOL_PASS", "")
        self.cookies = None
    async def search(self, origin: str, destination: str, date: str, **kwargs) -> List[Dict]:
        # Login if required
        pass
        # Discover endpoints from home
        driver = make_driver_cdp()
        try:
            driver.get("https://www.voegol.com.br/")
            wait_css(driver, "body", 30)
            endpoints = extract_json_endpoints(driver, host_hints=HOST_HINTS, source="gol")
        finally:
            driver.quit()
        results: List[Dict] = []
        async with make_client(None) as client:
            for url in endpoints[:8]:
                try:
                    r = await client.get(url, params={"from": origin, "to": destination, "date": date})
                    # Try JSON first
                    try:
                        data = r.json()
                    except Exception:
                        try:
                            data = json.loads(r.text)
                        except Exception:
                            continue
                    offers = data.get("offers") or data.get("flights") or data.get("data") or []
                    for it in offers:
                        price = float(it.get("price") or it.get("amount") or it.get("miles") or 0)
                        currency = it.get("currency") or "BRL"
                        cabin = it.get("cabin")
                        fare = "miles" if ("miles" in it or "gol cash" in ["connectmiles","smiles","latam","azul"]) else it.get("fareType")
                        results.append(
                            normalize_result(f"{origin}-{destination}", date, price,
                                             source="gol", currency=currency, program="GOL Cash",
                                             fare_type=fare, cabin=cabin, meta=it)
                        )
                except Exception as e:
                    logger.debug(f"[gol] endpoint trial failed: {e}")
        return results
