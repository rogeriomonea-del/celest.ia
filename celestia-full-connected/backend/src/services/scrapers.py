import asyncio
from services.http_client import fetch
from services.parsers import parse_prices_html_bs4, parse_prices_html_selectolax
from services.selenium_runner import run_example
from core.logging import logger

# HTTP scraper example (replace URL and params with program endpoints / meta-search results)
async def scrape_http_example(origin: str, destination: str, date: str) -> list[dict]:
    url = "https://example.com/search"  # placeholder
    params = {"from": origin, "to": destination, "date": date}
    html = await fetch(url, params=params)
    out = parse_prices_html_bs4(html)
    if not out:
        out = parse_prices_html_selectolax(html)
    # Self-healing approach: if both empty, try simplified params or alternate endpoint
    if not out:
        params.pop("date", None)
        html2 = await fetch(url, params=params)
        out = parse_prices_html_selectolax(html2)
    # Tag the source:
    for r in out:
        r["source"] = r.get("source") or "http-example"
    return out

def scrape_selenium_example(origin: str, destination: str, date: str) -> list[dict]:
    # Replace with a real site URL & selectors. This demonstrates headless selenium flow.
    url = "https://example.com/results"
    row_selector = ".result-item"
    price_selector = ".price"
    prices = run_example(url, row_selector, price_selector)
    return [{"route": f"{origin}-{destination}", "date": date, "price": float(p), "source": "selenium-example"} for p in prices if p and p.replace('.', '', 1).isdigit()]

async def fetch_prices(origin: str, destination: str, date: str) -> list[dict]:
    http_results = await scrape_http_example(origin, destination, date)
    selenium_results = scrape_selenium_example(origin, destination, date)
    return (http_results or []) + (selenium_results or [])
