from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

from retry import retry
from CommonCode.CustomExceptions import UIException
from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject


class InvariableFields(BaseTestObject):
    @retry(exceptions=(WebDriverException, UIException), delay=2, tries=15)
    def click(self):
        if not self.element:
            raise UIException('element does not exist')
        if not self.element.is_enabled():
            raise UIException('element is not enabled')
        if not self.element.is_displayed():
            raise UIException('element is not displayed')

        self.element.click()

    def text_content(self):
        return self.element.get_attribute('textContent')

    def enter_value(self, value):
        self.element.send_keys(value)

    def clear_field(self):
        self.element.clear()

    def tab_from_element(self):
        self.element.send_keys(Keys.TAB)

    def get_text(self):
        return self.element.get_attribute('innerHTML').strip()

    def get_text_no_whitespace(self):
        return " ".join(self.element.get_attribute('innerHTML').split())

    def return_text(self):
        return self.element.text

    def return_text_value_stripped(self):
        return self.element.text.replace(',', '').encode('ascii')

    def return_value(self):
        return self.element.get_attribute('value')

    def get_outer_html(self):
        return self.element.get_attribute('outerHTML')

    def get_text_value_stripped(self):
        return self.element.get_attribute('innerHTML').replace(",", "")

    def get_inner_text(self):
        return self.element.get_attribute('innerText')

    def get_inner_text_without_shifter(self):
        return self.element.get_attribute('innerText').replace("\n", "")

    def get_text_without_react(self):
        return self.element.get_attribute('innerHTML').split('<!-- /react-text')[0].split('-->')[1]

    def get_value(self):
        return self.element.get_attribute("value")

    def get_class(self):
        return self.element.get_attribute("className")

    def get_children_text(self):
        return self.element.find_element_by_tag_name("text")

    @property
    def text(self):
        return self.element.get_attribute("innerText").strip()

    @property
    def try_float(self):
        try:
            return float(self.get_inner_text().replace(',', ''))
        except ValueError:
            return None

    @property
    def text_with_no_with_spaces(self):
        return self.element.text.replace(" ", "")
