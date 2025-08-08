from typing import List, Dict
from services.selenium_cdp import make_driver_cdp, wait_css, extract_json_endpoints, get_cookies
from services.http_client_ex import make_client
from sources.common.normalize import normalize_result
from core.logging import logger
import os, json

HOST_HINTS = ["voeazul.com.br", "tudoazul.voeazul.com.br"]

class AzulScraper:
    def __init__(self):
        self.user = os.getenv("AZUL_USER", "")
        self.password = os.getenv("AZUL_PASS", "")
        self.cookies = None

    async def login(self):
        driver = make_driver_cdp()
        try:
            driver.get("https://tudoazul.voeazul.com.br/portal/pt/meu-perfil/login")
            wait_css(driver, 'input[type="email"], input#username', 30)
            driver.find_element("css selector",'input[type="email"], input#username').send_keys(self.user)
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
            driver.get("https://voeazul.com.br")
            wait_css(driver, "body", 30)
            endpoints = extract_json_endpoints(driver, host_hints=HOST_HINTS)
        finally:
            driver.quit()

        results: List[Dict] = []
        async with make_client(self.cookies) as client:
            for url in endpoints[:8]:
                try:
                    r = await client.get(url, params={"origin": origin, "destination": destination, "date": date})
                    data = r.json()
                    offers = data.get("offers") or data.get("flights") or []
                    for it in offers:
                        price = float(it.get("price") or it.get("amount") or 0)
                        currency = it.get("currency") or "BRL"
                        cabin = it.get("cabin")
                        results.append(normalize_result(f"{origin}-{destination}", date, price, source="azul", currency=currency, program="Azul", fare_type=it.get("fareType"), cabin=cabin, meta=it))
                except Exception as e:
                    logger.warning(f"AZUL endpoint trial failed: {e}")
        return results
