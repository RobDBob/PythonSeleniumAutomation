from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from CommonCode.TestExecute.Logging import PrintMessage


class NumericEditField(object):

    def __init__(self, webdriver, by_type=By.CSS_SELECTOR, value="div.menu.transition.visible input[type='number']",
                 index=0):
        self.element = webdriver.find_elements(by_type, value)[index]

    def clear(self):
        self.element.clear()

    def send_keys(self, value):
        self.clear()
        self.element.send_keys(value)

    def enter_value(self, value):
        self.element.click()
        self.element.clear()
        self.element.send_keys(value)
        self.element.send_keys(Keys.ENTER)
        PrintMessage('Value of %s entered.' % value)

    def click(self):
        self.element.click()

    def get_current_value(self):
        return self.element.get_attribute("value")

    @property
    def numeric_value(self):
        return int(self.get_current_value())

    @property
    def numeric_value_float(self):
        return int(float(self.get_current_value()))

    @property
    def numeric_value_no_commas(self):
        return int(self.get_current_value().replace(",", ""))
