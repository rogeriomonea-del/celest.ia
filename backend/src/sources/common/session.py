import httpx, random, asyncio
from typing import Optional
from core.config import settings

UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36",
]

def default_headers():
    return {"User-Agent": random.choice(UAS), "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

class HttpSession:
    def __init__(self, timeout: float | None = None, proxy: Optional[str] = None):
        self.timeout = timeout or settings.request_timeout if hasattr(settings, "request_timeout") else 30.0
        self.proxy = proxy or getattr(settings, "proxy_url", None)
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout, proxies=self.proxy, headers=default_headers(), follow_redirects=True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.aclose()

    async def get(self, url: str, params: dict | None = None):
        assert self.client
        return await self.client.get(url, params=params)

    async def post(self, url: str, data: dict | None = None, json: dict | None = None):
        assert self.client
        return await self.client.post(url, data=data, json=json)
