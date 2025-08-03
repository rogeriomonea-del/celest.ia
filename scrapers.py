"""Real web scrapers for Copa Airlines, ConnectMiles and Skyscanner.

The implementations rely only on the Python standard library. They are minimal
examples intended for educational use; always verify the terms of service of
any website before scraping.
"""
from __future__ import annotations

from typing import List
import re
import urllib.parse
import urllib.request

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    )
}


def _http_get(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")


def _http_post(url: str, data: dict) -> str:
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")


def scrape_copa_airlines(origin: str, destination: str, depart_date: str) -> List[str]:
    """Return flight prices from Copa Airlines search results."""

    url = (
        "https://www.copaair.com/en-us/flights/" f"{origin}-{destination}?departure={depart_date}"
    )
    html = _http_get(url)
    return re.findall(r'class="price">([^<]+)<', html)


def scrape_connect_miles(username: str, password: str) -> str:
    """Return mileage balance from ConnectMiles."""

    login_html = _http_get("https://www.connectmiles.com/login")
    token_match = re.search(r'name="csrf_token" value="([^"]+)"', login_html)
    token = token_match.group(1) if token_match else ""
    _http_post(
        "https://www.connectmiles.com/login",
        {"username": username, "password": password, "csrf_token": token},
    )
    account_html = _http_get("https://www.connectmiles.com/account")
    balance_match = re.search(r'id="available-miles">([^<]+)<', account_html)
    return balance_match.group(1).strip() if balance_match else ""


def scrape_skyscanner(origin: str, destination: str, depart_date: str) -> List[str]:
    """Return flight prices from Skyscanner search results."""

    url = (
        "https://www.skyscanner.com.br/transport/flights/" f"{origin}/{destination}/{depart_date}/"
    )
    html = _http_get(url)
    return re.findall(r'class="price">([^<]+)<', html)

