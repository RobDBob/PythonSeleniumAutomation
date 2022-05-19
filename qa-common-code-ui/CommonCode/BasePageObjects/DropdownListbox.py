from CommonCode.TestExecute.Logging import PrintMessage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject
from CommonCode.WebDriver import ExpectedConditions as EC


class OptionElement(object):
    def __init__(self, element):
        self.element = element

    def select_option(self):
        self.element.click()

    @property
    def option(self):
        option_text = self.element.get_attribute("innerText")
        return str(option_text).replace('\n', '')


class DropdownListbox(BaseTestObject):
    """
    Working off listbox (aria type)
    Instantiated object does not need those two and safe coded to work without
    This way we can bypass init.
    """

    def __init__(self,
                 parent_web_element,
                 by_type,
                 value,
                 index=0,
                 options_locator=(By.CSS_SELECTOR, 'div.item[role="option"]')):
        super().__init__(parent_web_element, by_type, value, index)

        self.options_locator = options_locator
        self.wait = None

    def wait_for_dropdown(self):
        wait_condition = EC.visibility_of_element_located(self.element)
        WebDriverWait(self.parent_web_element, 60).until(wait_condition)

    def get_available_options(self):
        all_options = self.element.find_elements(*self.options_locator)
        return [OptionElement(k) for k in all_options]

    def select_option(self, option):
        PrintMessage('Attempting to select option of %s...' % option)
        self.scroll_to_element()
        self.element.click()
        self.wait_for_dropdown()

        all_options = self.get_available_options()

        try:
            option_index = [k.option for k in all_options].index(option)
        except ValueError:
            PrintMessage("Option: {0} not found in {1}".format(option, self.element.text))
            raise
        PrintMessage('Option of %s has been selected.' % option)

        all_options[option_index].select_option()

        if self.wait:
            self.wait()

    @property
    def selected_option(self):
        return self.element.text

    @property
    def selected_data(self):
        return self.element.get_attribute("data-testid-selected")

    @property
    def current_value(self):
        return self.element.get_attribute("value")
