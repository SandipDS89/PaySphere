import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"


def _register_login_create_account(driver, email):
    """Helper: registers, logs in, and creates a wallet account through the real UI."""
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.NAME, "name").send_keys("Selenium Wallet User")
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys("test123")
    driver.find_element(By.NAME, "confirm_password").send_keys("test123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains("/login"))

    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys("test123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    wait.until(EC.url_contains("/dashboard"))

    # Click "Create My Account"
    driver.find_element(By.LINK_TEXT, "Create My Account").click()
    wait.until(EC.url_contains("/dashboard"))


def test_deposit_updates_balance():
    driver = webdriver.Chrome()
    try:
        random_id = random.randint(10000, 99999)
        email = f"selenium_deposit_{random_id}@example.com"

        _register_login_create_account(driver, email)

        # Go to Deposit page
        driver.get(f"{BASE_URL}/deposit")
        driver.find_element(By.NAME, "amount").send_keys("750")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("/dashboard"))

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "750.00" in page_text or "₹750.00" in page_text

    finally:
        driver.quit()


def test_withdraw_more_than_balance_shows_error():
    driver = webdriver.Chrome()
    try:
        random_id = random.randint(10000, 99999)
        email = f"selenium_withdraw_{random_id}@example.com"

        _register_login_create_account(driver, email)
        # Balance is ₹0.00 fresh — any withdrawal should fail

        driver.get(f"{BASE_URL}/withdraw")
        driver.find_element(By.NAME, "amount").send_keys("100")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))

        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Insufficient balance" in page_text

    finally:
        driver.quit()