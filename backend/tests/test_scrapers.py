import asyncio
from services.parsers import parse_prices_html_bs4, parse_prices_html_selectolax

def test_parsers_empty():
    assert parse_prices_html_bs4("<html></html>") == []
    assert parse_prices_html_selectolax("<html></html>") == []

def test_parsers_basic():
    html = '<div class="result-item"><span class="price">R$ 1.234</span></div>'
    r1 = parse_prices_html_bs4(html)
    r2 = parse_prices_html_selectolax(html)
    assert isinstance(r1, list)
    assert isinstance(r2, list)
