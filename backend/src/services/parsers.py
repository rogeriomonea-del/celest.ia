from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

def parse_prices_html_bs4(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    # Example generic scraping — replace with site-specific selectors:
    for item in soup.select("[data-flight-row], .flight-row, .result-item"):
        route = (item.get("data-route") or "").upper()
        date = (item.get("data-date") or "")
        price_txt = (item.select_one(".price, [data-price]") or {}).get_text(strip=True) if hasattr(item.select_one(".price, [data-price]"), "get_text") else None
        if price_txt:
            price = float("".join(ch for ch in price_txt if ch.isdigit() or ch == "."))
            out.append({"route": route, "date": date, "price": price, "source": "http-parser"})
    return out

def parse_prices_html_selectolax(html: str) -> list[dict]:
    tree = HTMLParser(html)
    out = []
    for node in tree.css(".flight-row, .result-item"):
        price_node = node.css_first(".price")
        if price_node:
            text = price_node.text(strip=True)
            digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
            if digits:
                out.append({"route": "", "date": "", "price": float(digits), "source": "selectolax"})
    return out
