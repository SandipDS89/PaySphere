from selenium.webdriver.common.by import By
from .base_page import BasePage, BASE_URL


class RegisterPage(BasePage):
    URL = f"{BASE_URL}/register"

    # Locators - defined once, used everywhere
    NAME_INPUT = (By.NAME, "name")
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    CONFIRM_PASSWORD_INPUT = (By.NAME, "confirm_password")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")

    def load(self):
        self.driver.get(self.URL)
        return self

    def register(self, name, email, password, confirm_password=None):
        """Fills and submits the registration form in one call."""
        if confirm_password is None:
            confirm_password = password

        self.driver.find_element(*self.NAME_INPUT).send_keys(name)
        self.driver.find_element(*self.EMAIL_INPUT).send_keys(email)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.CONFIRM_PASSWORD_INPUT).send_keys(confirm_password)
        self.driver.find_element(*self.SUBMIT_BUTTON).click()
        return self