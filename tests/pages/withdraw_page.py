from selenium.webdriver.common.by import By
from .base_page import BasePage, BASE_URL


class WithdrawPage(BasePage):
    URL = f"{BASE_URL}/withdraw"

    AMOUNT_INPUT = (By.NAME, "amount")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")

    def load(self):
        self.driver.get(self.URL)
        return self

    def withdraw(self, amount):
        self.driver.find_element(*self.AMOUNT_INPUT).send_keys(str(amount))
        self.driver.find_element(*self.SUBMIT_BUTTON).click()
        return self