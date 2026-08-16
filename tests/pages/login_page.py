from selenium.webdriver.common.by import By
from .base_page import BasePage, BASE_URL


class LoginPage(BasePage):
    URL = f"{BASE_URL}/login"

    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")

    def load(self):
        self.driver.get(self.URL)
        return self

    def login(self, email, password):
        self.driver.find_element(*self.EMAIL_INPUT).send_keys(email)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.SUBMIT_BUTTON).click()
        return self