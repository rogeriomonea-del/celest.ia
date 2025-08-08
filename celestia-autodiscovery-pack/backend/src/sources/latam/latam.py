from typing import List, Dict
from services.selenium_cdp import make_driver_cdp, wait_css, extract_json_endpoints, get_cookies
from services.http_client_ex import make_client
from sources.common.normalize import normalize_result
from core.logging import logger
import os, json

HOST_HINTS = ["latamairlines.com", "latam.com"]

class LatamScraper:
    def __init__(self):
        self.user = os.getenv("LATAM_USER", "")
        self.password = os.getenv("LATAM_PASS", "")
        self.cookies = None

    async def login(self):
        # Minimal Selenium login; selectors may need adjustment
        driver = make_driver_cdp()
        try:
            driver.get("https://www.latamairlines.com/br/pt_br/login")
            wait_css(driver, 'input[type="email"]', 30)
            driver.find_element("css selector",'input[type="email"]').send_keys(self.user)
            driver.find_element("css selector",'input[type="password"]').send_keys(self.password)
            driver.find_element("css selector",'button[type="submit"]').click()
            wait_css(driver, "body", 30)
            self.cookies = get_cookies(driver)
        finally:
            driver.quit()

    async def search(self, origin: str, destination: str, date: str, **kwargs) -> List[Dict]:
        # Try HTTP API post-login via endpoint auto-discovery
        if not self.cookies:
            await self.login()
        # quick pass: load a search page to populate network log endpoints
        driver = make_driver_cdp()
        try:
            driver.get("https://www.latamairlines.com/br/pt_br")
            wait_css(driver, "body", 30)
            endpoints = extract_json_endpoints(driver, host_hints=HOST_HINTS)
        finally:
            driver.quit()

        results: List[Dict] = []
        async with make_client(self.cookies) as client:
            for url in endpoints[:8]:
                try:
                    r = await client.get(url, params={"from": origin, "to": destination, "date": date})
                    if r.headers.get("content-type","").startswith("application/json"):
                        data = r.json()
                    else:
                        try:
                            data = json.loads(r.text)
                        except Exception:
                            continue
                    offers = data.get("offers") or data.get("data") or []
                    for it in offers:
                        price = float(it.get("price") or it.get("amount") or 0)
                        currency = it.get("currency") or "BRL"
                        cabin = it.get("cabin")
                        results.append(normalize_result(f"{origin}-{destination}", date, price, source="latam", currency=currency, program="LATAM", fare_type=it.get("fareType"), cabin=cabin, meta=it))
                except Exception as e:
                    logger.warning(f"LATAM endpoint trial failed: {e}")
        return results
