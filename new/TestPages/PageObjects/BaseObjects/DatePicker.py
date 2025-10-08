from datetime import date, datetime
from retry import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from CommonCode.CustomExceptions import UIException
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.EditField import EditField


class DatePicker(BaseTestObject):
    """
    Class currently defaults to UK date format
    see: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    """
    DATE_FORMAT = "%d/%m/%Y"

    def clearContent(self):
        self.dateEdit.click()
        content = self.dateEdit.value
        for _ in content:
            self.dateEdit.send_keys(Keys.BACKSPACE)

    def _typeInNewDate(self, value):
        self.clearContent()
        self.dateEdit.send_keys(value, clear=False)
        self.dateEdit.send_keys(Keys.ENTER, clear=False)

    # pylint: disable=invalid-name
    @retry(exceptions=UIException, delay=2, tries=4)
    def specify_date(self, value, clickParent=False):
        if isinstance(value, date):
            value = value.strftime(self.DATE_FORMAT)

        self._typeInNewDate(value)

        PrintMessage(f"Date is set to: {value}. Actual value: {self.dateEdit.value}", inStepMessage=True)

        if value != self.dateEdit.value:
            raise UIException
        self.dateEdit.send_keys(Keys.TAB, clear=False)

        if clickParent:
            # Experimental to close calendar form
            self.parentElement.click()

    @property
    def dateEdit(self):
        return EditField(self.webdriver, self.element, By.XPATH, './/input')

    @property
    def date(self):
        currentValue = self.dateEdit.value
        return datetime.strptime(currentValue, self.DATE_FORMAT)
