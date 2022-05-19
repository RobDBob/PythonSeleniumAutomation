from CommonCode.TestExecute.Logging import PrintMessage
from selenium.webdriver.common.by import By

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject
from CommonCode.BasePageObjects.Labels import Label
from CommonCode.PageEnums import CheckboxState


class CheckBox(BaseTestObject):
    def clear(self):
        self.element.clear()

    def click(self):
        self.element.click()
        PrintMessage('Checkbox toggled.')

    def get_current_value(self):
        return self.element.get_attribute("value")

    def get_placeholder_text(self):
        return self.element.get_attribute("placeholder")

    @property
    def text(self):
        return self.element.text

    @property
    def checked(self):
        return CheckboxState.checked in self.element.get_attribute('class')

    @property
    def is_checked(self):
        return bool(self.element.get_attribute('checked'))

    @property
    def label(self):
        return Label(self.element, By.CSS_SELECTOR, 'label')
