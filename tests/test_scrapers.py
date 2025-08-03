import scrapers


def test_scrape_copa_airlines(monkeypatch):
    html = '<div class="price">$100</div><div class="price">$200</div>'
    monkeypatch.setattr(scrapers, "_http_get", lambda url: html)
    prices = scrapers.scrape_copa_airlines("AAA", "BBB", "2024-01-01")
    assert prices == ["$100", "$200"]


def test_scrape_skyscanner(monkeypatch):
    html = '<span class="price">R$300</span>'
    monkeypatch.setattr(scrapers, "_http_get", lambda url: html)
    prices = scrapers.scrape_skyscanner("AAA", "BBB", "2024-01-01")
    assert prices == ["R$300"]


def test_scrape_connect_miles(monkeypatch):
    login_html = '<input name="csrf_token" value="token123">'
    account_html = '<div id="available-miles">12345</div>'

    def fake_get(url: str) -> str:
        if "login" in url:
            return login_html
        return account_html

    posted = {}

    def fake_post(url: str, data: dict) -> str:
        posted.update(data)
        return ""

    monkeypatch.setattr(scrapers, "_http_get", fake_get)
    monkeypatch.setattr(scrapers, "_http_post", fake_post)
    balance = scrapers.scrape_connect_miles("user", "pass")
    assert balance == "12345"
    assert posted["username"] == "user"
    assert posted["password"] == "pass"
    assert posted["csrf_token"] == "token123"
