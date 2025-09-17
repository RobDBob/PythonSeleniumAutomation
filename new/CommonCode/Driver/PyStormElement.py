from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from CommonCode.CustomExceptions import UIException


class PyStormElement(WebElement):
    findByType = None
    findByValue = None

    def _updateLocator(self, foundElement, by, value):
        foundElement.findByType = by
        foundElement.findByValue = value
        return foundElement

    def find_elements(self, by=By.ID, value=None):
        """
        Find elements given a By strategy and locator. Prefer the find_elements_by_* methods when
        possible.

        :Usage:
            elements = driver.find_elements(By.CLASS_NAME, 'foo')

        :rtype: list of WebElement
        """
        return [self._updateLocator(k, by, value) for k in super().find_elements(by, value)]

    def find_element(self, by=By.ID, value=None):
        """
        Find an element given a By strategy and locator. Prefer the find_element_by_* methods when
        possible.

        :Usage:
            element = driver.find_element(By.ID, 'foo')

        :rtype: WebElement
        """
        elements = self.find_elements(by, value)

        if len(elements) > 0:
            return elements[0]
        return None

    def checkIfClickable(self):
        if self.is_enabled() and self.is_displayed():
            return
        raise UIException(f"Element clickable: '{self.is_enabled()}', or visible: '{self.is_displayed()}'")

    def click(self):
        self.checkIfClickable()
        super().click()

    @property
    def isHidden(self):
        return "display" in self.get_attribute("style") and "none" in self.get_attribute("style")
