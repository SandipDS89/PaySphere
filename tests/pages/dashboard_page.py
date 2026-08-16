from selenium.webdriver.common.by import By
from .base_page import BasePage, BASE_URL


class DashboardPage(BasePage):
    URL = f"{BASE_URL}/dashboard"

    CREATE_ACCOUNT_LINK = (By.LINK_TEXT, "Create My Account")

    def load(self):
        self.driver.get(self.URL)
        return self

    def create_account(self):
        self.driver.find_element(*self.CREATE_ACCOUNT_LINK).click()
        return self