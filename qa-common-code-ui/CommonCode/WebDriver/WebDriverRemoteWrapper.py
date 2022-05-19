from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from CommonCode.WebDriver.ElementFinder import update_locator
from CommonCode.WebDriver.WebElementWrapper import WebElementWrapper


class WebDriverRemoteWrapper(WebDriver):
    _web_element_cls = WebElementWrapper

    def find_elements(self, by=By.ID, value=None):
        """
        Find elements given a By strategy and locator. Prefer the find_elements_by_* methods when
        possible.

        :Usage:
            elements = driver.find_elements(By.CLASS_NAME, 'foo')

        :rtype: list of WebElement
        """
        new_by, new_value = update_locator(by, value)
        return super().find_elements(new_by, new_value)

    def find_element(self, by=By.ID, value=None, index=0):
        """
        Find an element given a By strategy and locator. Prefer the find_element_by_* methods when
        possible.

        :Usage:
            element = driver.find_element(By.ID, 'foo')

        :rtype: WebElement
        """
        elements = self.find_elements(by, value)

        if len(elements) > index:
            return elements[index]
        else:
            return None
