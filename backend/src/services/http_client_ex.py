import httpx
from httpx import Cookies
from core.logging import logger
from core.config import settings

def make_client(cookies: dict[str,str] | None = None) -> httpx.AsyncClient:
    hdrs = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
        "Accept": "application/json, text/plain, */*",
    }
    jar = Cookies()
    if cookies:
        for k,v in cookies.items():
            jar.set(k, v)
    return httpx.AsyncClient(headers=hdrs, timeout=settings.request_timeout, proxies=settings.proxy_url, cookies=jar, follow_redirects=True)
