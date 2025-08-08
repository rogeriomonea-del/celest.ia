from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.logging import logger
import os, json, time

def make_driver_cdp():
    caps = DesiredCapabilities.CHROME.copy()
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    opts = Options()
    opts.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1366,768")
    driver = webdriver.Chrome(options=opts, desired_capabilities=caps)
    return driver

def wait_css(driver, selector: str, timeout: int = 30):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

def get_network_events(driver):
    logs = driver.get_log('performance')
    for entry in logs:
        try:
            yield json.loads(entry['message'])['message']
        except Exception:
            continue

def extract_json_endpoints(driver, host_hints: list[str] | None = None):
    endpoints = []
    for msg in get_network_events(driver):
        method = msg.get('method')
        if method in ('Network.responseReceived', 'Network.requestWillBeSent'):
            params = msg.get('params', {})
            req = params.get('request', {})
            url = (req.get('url') or params.get('response', {}).get('url') or "")
            if not url:
                continue
            if host_hints and not any(h in url for h in host_hints):
                continue
            # heuristic: likely API if json or has 'api' in path or ?search / offers etc.
            if any(k in url.lower() for k in ['api', 'search', 'availability', 'offers', 'award', 'miles']):
                endpoints.append(url)
    # de-dup preserving order
    seen = set()
    out = []
    for u in endpoints:
        if u not in seen:
            out.append(u); seen.add(u)
    return out

def get_cookies(driver):
    return {c['name']: c['value'] for c in driver.get_cookies()}
