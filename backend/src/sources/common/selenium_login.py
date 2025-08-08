from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from services.selenium_runner import make_driver, wait_css
from core.logging import logger

def login_and_get_cookies(url: str, username: str, password: str, user_sel: str, pass_sel: str, submit_sel: str, wait_after: str = "body"):
    driver = make_driver()
    try:
        driver.get(url)
        wait_css(driver, user_sel, 30)
        driver.find_element(By.CSS_SELECTOR, user_sel).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, pass_sel).send_keys(password)
        driver.find_element(By.CSS_SELECTOR, submit_sel).click()
        wait_css(driver, wait_after, 30)
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        return cookies
    finally:
        driver.quit()
