import random
from selenium import webdriver
from tests.pages.register_page import RegisterPage
import pytest
pytestmark = pytest.mark.selenium

def test_register_page_loads():
    driver = webdriver.Chrome()
    try:
        page = RegisterPage(driver).load()
        heading = driver.find_element("tag name", "h2")
        assert "Create your PaySphere account" in heading.text
    finally:
        driver.quit()


def test_successful_registration_via_browser():
    driver = webdriver.Chrome()
    try:
        random_id = random.randint(10000, 99999)
        test_email = f"selenium_test_{random_id}@example.com"

        page = RegisterPage(driver).load()
        page.register("Selenium Test User", test_email, "test123")
        page.wait_for_url_contains("/login")

        assert "Registration successful" in page.get_body_text()

    finally:
        driver.quit()


def test_registration_with_mismatched_passwords():
    driver = webdriver.Chrome()
    try:
        random_id = random.randint(10000, 99999)

        page = RegisterPage(driver).load()
        page.register(
            "Mismatch Test",
            f"mismatch_{random_id}@example.com",
            "test123",
            confirm_password="different456"
        )

        # Wait for the flash message (alert box) to actually appear
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        page.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))

        assert "Passwords do not match" in page.get_body_text()

    finally:
        driver.quit()