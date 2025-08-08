from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.logging import logger
import os, time

def make_driver():
    opts = Options()
    opts.binary_location = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(options=opts)
    return driver

def wait_css(driver, selector: str, timeout: int = 20):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

def safe_get_text(e):
    try:
        return e.text.strip()
    except Exception:
        return ""

def run_example(url: str, row_selector: str, price_selector: str):
    driver = make_driver()
    try:
        driver.get(url)
        wait_css(driver, row_selector, 30)
        rows = driver.find_elements(By.CSS_SELECTOR, row_selector)
        out = []
        for r in rows[:10]:
            price_el = r.find_element(By.CSS_SELECTOR, price_selector)
            price = safe_get_text(price_el).replace("R$", "").replace(",", ".").strip()
            out.append(price)
        return out
    finally:
        driver.quit()
