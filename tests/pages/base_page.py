from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def get_body_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text

    def current_url(self):
        return self.driver.current_url

    def wait_for_url_contains(self, fragment):
        self.wait.until(EC.url_contains(fragment))