from CommonCode.CustomExceptions import UIException
from retry import retry
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject


class Button(BaseTestObject):
    def get_title(self):
        return self.element.get_attribute('title')

    def get_text(self):
        return self.element.get_attribute('innerHTML')

    def get_inner_text_without_shifter(self):
        return self.element.get_attribute('innerText').replace("\n", "")

    def get_inner_text(self):
        return self.element.get_attribute('innerText')

    def hover_over(self):
        hover = ActionChains(self.element).move_to_element(self.element)
        hover.perform()

    @property
    def is_disabled(self):
        return self.get_attribute('disabled')

    @property
    def is_active(self):
        """
        Some buttons when clicked, become active i.e. active class is added to element
        This property indicates if button was already clicked
        :return:
        """
        return 'active' in self.element.get_attribute('class')

    @retry(exceptions=(WebDriverException, UIException), delay=2, tries=15)
    def click(self):
        if not self.element:
            raise UIException('element does not exist')
        if not self.element.is_enabled():
            raise UIException('element is not enabled')
        if not self.element.is_displayed():
            raise UIException('element is not displayed')

        self.element.click()

    @property
    def text(self):
        return self.element.get_attribute('innerHTML').strip()

    @property
    def text_only(self):
        return self.element.get_attribute('textContent')
