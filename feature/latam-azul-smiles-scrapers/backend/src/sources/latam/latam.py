from typing import List, Dict, Optional
from sources.common.selenium_login import login_and_get_cookies
from sources.common.session import HttpSession
from sources.common.normalize import normalize_result
from core.logging import logger
import os, json, time

LOGIN_URL = "https://www.latamairlines.com/br/pt_br/login"  # may redirect
SEARCH_URL = "https://www.latamairlines.com/br/pt_br/flights"  # public search page (SSR/CSR mix)
# Example authenticated API endpoint (placeholder; adjust to real endpoint captured from devtools)
API_URL = "https://www.latamairlines.com/api/some/search"     # TODO: set real URL

class LatamScraper:
    def __init__(self):
        self.user = os.getenv("LATAM_USER", "")
        self.password = os.getenv("LATAM_PASS", "")
        self.cookies: dict[str,str] | None = None

    async def login(self) -> None:
        if not self.user or not self.password:
            logger.warning("LATAM creds not set; skipping login.")
            self.cookies = None
            return
        self.cookies = login_and_get_cookies(
            url=LOGIN_URL,
            username=self.user,
            password=self.password,
            user_sel='input[name="email"]',
            pass_sel='input[name="password"]',
            submit_sel='button[type="submit"]',
            wait_after='body',
        )

    async def search(self, origin: str, destination: str, date: str, **kwargs) -> List[Dict]:
        # Try authenticated API first if cookies present; else fallback to public HTML
        out: List[Dict] = []
        async with HttpSession() as s:
            if self.cookies:
                try:
                    # Attempt API call with cookies (placeholder; update headers/cookies)
                    r = await s.get(API_URL, params={"from": origin, "to": destination, "date": date})
                    if r.status_code == 200 and r.text.strip().startswith("{"):
                        data = json.loads(r.text)
                        # TODO: adapt to real JSON shape
                        for it in (data.get("offers") or []):
                            price = float(it.get("price", 0))
                            currency = it.get("currency", "BRL")
                            cabin = it.get("cabin", None)
                            out.append(normalize_result(f"{origin}-{destination}", date, price,
                                                        source="latam", currency=currency, program="LATAM",
                                                        fare_type=it.get("fare_type"), cabin=cabin, meta=it))
                        if out:
                            return out
                except Exception as e:
                    logger.warning(f"LATAM API attempt failed: {e}")

            # Fallback: public HTML page (will likely need selector-based parsing)
            try:
                r2 = await s.get(SEARCH_URL, params={"from": origin, "to": destination, "date": date})
                r2.raise_for_status()
                # TODO: parse HTML with BeautifulSoup/selectolax (needs real selectors)
                # For now, return empty to allow orchestrator fallback
                return out
            except Exception as e:
                logger.warning(f"LATAM HTML attempt failed: {e}")
                return out
