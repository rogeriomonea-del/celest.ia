import httpx
import random
import asyncio
from core.config import settings
from core.logging import logger

UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
]

def _headers():
    return {
        "User-Agent": random.choice(UAS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

async def fetch(url: str, params: dict | None = None) -> str:
    timeout = settings.request_timeout
    retries = settings.max_retries
    proxy = settings.proxy_url

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout, proxies=proxy) as client:
                r = await client.get(url, params=params, headers=_headers(), follow_redirects=True)
                r.raise_for_status()
                return r.text
        except Exception as e:
            logger.warning(f"[HTTP] attempt {attempt}/{retries} failed for {url}: {e}")
            await asyncio.sleep(1.5 * attempt)
    raise RuntimeError(f"HTTP fetch failed after {retries} attempts: {url}")
