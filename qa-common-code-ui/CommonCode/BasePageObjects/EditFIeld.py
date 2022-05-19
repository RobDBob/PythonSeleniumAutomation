import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject
from CommonCode.TestExecute.Logging import PrintMessage


class EditField(BaseTestObject):
    def clear(self):
        self.element.clear()

    def click(self):
        self.element.click()

    def enter_value(self, value):
        self.element.click()
        self.element.clear()
        self.element.send_keys(value)
        self.element.send_keys(Keys.ENTER)
        PrintMessage('Value of %s entered.' % value)

    def send_keys(self, value, clear=True):
        if clear:
            self.clear()
        self.element.send_keys(value)

    def send_keys_slowly(self, value, clear=True):
        if clear:
            self.clear()
        for character in value:
            self.element.send_keys(character)
            time.sleep(0.05)

    def get_placeholder_text(self):
        return self.element.get_attribute("placeholder")

    @property
    def value(self):
        return self.element.get_attribute("value")

    @property
    def text(self):
        return self.element.get_attribute("innerText")


class NumericEditField(EditField):
    @property
    def numeric_value(self):
        return int(self.value)


class EditFieldByID(object):

    def __init__(self, entity):
        self.element = entity.find_element(By.CSS_SELECTOR, "div[role='combobox']").find_element(By.CLASS_NAME,
                                                                                                 'search')

    def clear(self):
        self.element.clear()

    def send_keys(self, value):
        self.clear()
        self.element.send_keys(value)

    def click(self):
        self.element.click()

    def get_current_value(self):
        return self.element.get_attribute("value")

    def get_placeholder_text(self):
        return self.element.get_attribute("placeholder")

    def get_current_type(self):
        return self.element.get_attribute("type")
