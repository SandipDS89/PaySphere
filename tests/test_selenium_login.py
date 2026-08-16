import random
from selenium import webdriver
from tests.pages.register_page import RegisterPage
from tests.pages.login_page import LoginPage
import pytest
pytestmark = pytest.mark.selenium


def _register_via_browser(driver, email, password="test123"):
    page = RegisterPage(driver).load()
    page.register("Selenium Login Test", email, password)
    page.wait_for_url_contains("/login")


def test_login_valid_credentials():
    driver = webdriver.Chrome()
    try:
        random_id = random.randint(10000, 99999)
        email = f"selenium_login_{random_id}@example.com"

        _register_via_browser(driver, email)

        login_page = LoginPage(driver)
        login_page.login(email, "test123")
        login_page.wait_for_url_contains("/dashboard")

        assert "Welcome" in login_page.get_body_text()
        assert "/dashboard" in login_page.current_url()

    finally:
        driver.quit()


def test_login_invalid_password():
    driver = webdriver.Chrome()
    try:
        random_id = random.randint(10000, 99999)
        email = f"selenium_badlogin_{random_id}@example.com"

        _register_via_browser(driver, email)

        login_page = LoginPage(driver)
        login_page.login(email, "wrongpassword")

        # Wait for the flash message to actually appear before reading the page
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        login_page.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))

        assert "Invalid email or password" in login_page.get_body_text()
        assert "/dashboard" not in login_page.current_url()

    finally:
        driver.quit()


def test_dashboard_redirects_when_not_logged_in():
    driver = webdriver.Chrome()
    try:
        from tests.pages.dashboard_page import DashboardPage
        page = DashboardPage(driver).load()
        page.wait_for_url_contains("/login")

        assert "/login" in page.current_url()

    finally:
        driver.quit()