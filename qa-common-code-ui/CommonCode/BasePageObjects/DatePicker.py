from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject
from CommonCode.BasePageObjects.CTAButton import Button
from CommonCode.BasePageObjects.EditFIeld import EditField
from CommonCode.CustomExceptions import UIException
from retry import retry
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.WebDriver import ExpectedConditions as EC
from selenium.common.exceptions import TimeoutException


class DatePicker(BaseTestObject):
    """
    Class currently defaults to UK date format
    see: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    """
    date_format = "%m/%d/%Y"

    def wait_for_dimmer(self):
        dimmer_css_locator = '.ui.large.inverted.loader'

        try:
            PrintMessage('Waiting for filter to be applied...')
            dimmer_element = EC.presence_of_element_located((By.CSS_SELECTOR, dimmer_css_locator))
            WebDriverWait(self.parent_web_element, 3).until(dimmer_element)
        except TimeoutException:
            #  if we time-out then assume element disappeared before framework found it
            PrintMessage("TIMED-OUT: Missed element in FilterOperationElement > wait_for_dimmer")
            pass

        dimmer_element = EC.invisibility_of_element_located((By.CSS_SELECTOR, dimmer_css_locator))
        WebDriverWait(self.parent_web_element, 60).until(dimmer_element)

    def wait_for_value(self, expected_value):
        value_waiter = EC.text_to_be_present_in_element_value(self.date_edit, expected_value)
        WebDriverWait(self.parent_web_element, 60).until(value_waiter)

    def clear_content(self):
        self.date_edit.click()
        content = self.date_edit.value
        for _ in content:
            self.date_edit.send_keys(Keys.BACKSPACE)

    def _type_in_new_date(self, value):
        self.clear_content()
        self.date_edit.send_keys(value, clear=False)
        self.date_edit.send_keys(Keys.ENTER, clear=False)
        self.wait_for_dimmer()
        self.wait_for_value(value)

    @retry(exceptions=UIException, delay=2, tries=3)
    def specify_date(self, value):
        if isinstance(value, datetime):
            value = value.strftime(self.date_format)

        self._type_in_new_date(value)

        PrintMessage('Date is set to: {0}. Actual value: {1}'.format(value, self.date_edit.value))

        if value != self.date_edit.value:
            raise UIException

    @property
    def reset_to_default(self):
        return Button(self.element, By.CLASS_NAME, 'close-icon')

    @property
    def date_edit(self):
        return EditField(self.element, By.CSS_SELECTOR, 'input')

    @property
    def date(self):
        current_value = self.date_edit.value
        return datetime.strptime(current_value, self.date_format)
