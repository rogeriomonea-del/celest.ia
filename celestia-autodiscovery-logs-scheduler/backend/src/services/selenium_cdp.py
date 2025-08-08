from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.logging import logger
import os, json, time, pathlib, datetime

LOG_DIR = os.getenv("CDP_LOG_DIR", "logs/cdp")
pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

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
    return webdriver.Chrome(options=opts, desired_capabilities=caps)

def wait_css(driver, selector: str, timeout: int = 30):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

def _network_events(driver):
    logs = driver.get_log('performance')
    for entry in logs:
        try:
            yield json.loads(entry['message'])['message']
        except Exception:
            continue

def extract_json_endpoints(driver, host_hints: list[str] | None = None, *, source: str = "unknown"):
    endpoints = []
    for msg in _network_events(driver):
        method = msg.get('method')
        if method in ('Network.responseReceived', 'Network.requestWillBeSent'):
            params = msg.get('params', {})
            req = params.get('request', {})
            url = (req.get('url') or params.get('response', {}).get('url') or "")
            if not url:
                continue
            if host_hints and not any(h in url for h in host_hints):
                continue
            lo = url.lower()
            if any(k in lo for k in ['api', 'search', 'availability', 'offers', 'award', 'miles', 'fare', 'price']):
                endpoints.append(url)
    out, seen = [], set()
    for u in endpoints:
        if u not in seen:
            out.append(u); seen.add(u)

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    fname = os.path.join(LOG_DIR, f"cdp_{{source}}_{{stamp}}.json")
    try:
        with open(fname, "w") as f:
            json.dump(out, f, indent=2)
        logger.info(f"[CDP] Saved endpoints for {{source}} -> {{fname}} ({{len(out)}} URLs)")
    except Exception as e:
        logger.warning(f"[CDP] Failed to save endpoints log: {{e}}")

    return out

def get_cookies(driver):
    return {c['name']: c['value'] for c in driver.get_cookies()}
