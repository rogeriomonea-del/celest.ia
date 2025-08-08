from typing import List, Dict, Optional
from sources.common.selenium_login import login_and_get_cookies
from sources.common.session import HttpSession
from sources.common.normalize import normalize_result
from core.logging import logger
import os, json

LOGIN_URL = "https://www.smiles.com.br/login"  # may change
SEARCH_URL = "https://www.smiles.com.br/home"  # placeholder
API_URL = "https://api.smiles.com.br/some/search"  # TODO: real endpoint

class SmilesScraper:
    def __init__(self):
        self.user = os.getenv("SMILES_USER", "")
        self.password = os.getenv("SMILES_PASS", "")
        self.cookies: dict[str,str] | None = None

    async def login(self) -> None:
        if not self.user or not self.password:
            self.cookies = None
            return
        self.cookies = login_and_get_cookies(
            url=LOGIN_URL,
            username=self.user,
            password=self.password,
            user_sel='input[name="login"], input#login',
            pass_sel='input[name="password"], input#password',
            submit_sel='button[type="submit"], button.login__submit',
            wait_after='body',
        )

    async def search(self, origin: str, destination: str, date: str, **kwargs) -> List[Dict]:
        out: List[Dict] = []
        async with HttpSession() as s:
            if self.cookies:
                try:
                    r = await s.get(API_URL, params={"from": origin, "to": destination, "date": date})
                    if r.status_code == 200 and r.text.strip().startswith("{"):
                        data = json.loads(r.text)
                        for it in (data.get("offers") or []):
                            price = float(it.get("price", 0))
                            currency = it.get("currency", "BRL")
                            cabin = it.get("cabin", None)
                            out.append(normalize_result(f"{origin}-{destination}", date, price,
                                                        source="smiles", currency=currency, program="Smiles",
                                                        fare_type=it.get("fare_type"), cabin=cabin, meta=it))
                        if out:
                            return out
                except Exception as e:
                    logger.warning(f"SMILES API attempt failed: {e}")

            try:
                r2 = await s.get(SEARCH_URL, params={"from": origin, "to": destination, "date": date})
                r2.raise_for_status()
                return out
            except Exception as e:
                logger.warning(f"SMILES HTML attempt failed: {e}")
                return out
