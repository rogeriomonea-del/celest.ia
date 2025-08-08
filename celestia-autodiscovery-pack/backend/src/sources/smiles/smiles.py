from typing import List, Dict
from services.selenium_cdp import make_driver_cdp, wait_css, extract_json_endpoints, get_cookies
from services.http_client_ex import make_client
from sources.common.normalize import normalize_result
from core.logging import logger
import os, json

HOST_HINTS = ["smiles.com.br", "api.smiles.com.br", "gol.com"]

class SmilesScraper:
    def __init__(self):
        self.user = os.getenv("SMILES_USER", "")
        self.password = os.getenv("SMILES_PASS", "")
        self.cookies = None

    async def login(self):
        driver = make_driver_cdp()
        try:
            driver.get("https://www.smiles.com.br/login")
            wait_css(driver, 'input[type="email"], input#login', 30)
            driver.find_element("css selector",'input[type="email"], input#login').send_keys(self.user)
            driver.find_element("css selector",'input[type="password"], input#password').send_keys(self.password)
            driver.find_element("css selector",'button[type="submit"]').click()
            wait_css(driver, "body", 30)
            self.cookies = get_cookies(driver)
        finally:
            driver.quit()

    async def search(self, origin: str, destination: str, date: str, **kwargs) -> List[Dict]:
        if not self.cookies:
            await self.login()
        driver = make_driver_cdp()
        try:
            driver.get("https://www.smiles.com.br/home")
            wait_css(driver, "body", 30)
            endpoints = extract_json_endpoints(driver, host_hints=HOST_HINTS)
        finally:
            driver.quit()

        results: List[Dict] = []
        async with make_client(self.cookies) as client:
            for url in endpoints[:8]:
                try:
                    r = await client.get(url, params={"from": origin, "to": destination, "date": date})
                    data = r.json()
                    offers = data.get("offers") or data.get("flights") or []
                    for it in offers:
                        price = float(it.get("price") or it.get("amount") or it.get("miles") or 0)
                        currency = it.get("currency") or "BRL"
                        cabin = it.get("cabin")
                        fare = "miles" if "miles" in it else it.get("fareType")
                        results.append(normalize_result(f"{origin}-{destination}", date, price, source="smiles", currency=currency, program="Smiles", fare_type=fare, cabin=cabin, meta=it))
                except Exception as e:
                    logger.warning(f"SMILES endpoint trial failed: {e}")
        return results
