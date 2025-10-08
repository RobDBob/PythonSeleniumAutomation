from typing import Callable
from retry import retry
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from CommonCode.CustomExceptions import UIException
from CommonCode.Driver.PyStormDriver import PyStormDriver
from CommonCode.Driver.PyStormElement import PyStormElement
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.StateCallbacks import defaultIsCheckedCB


class CheckBox(BaseTestObject):
    isCheckedFuncCB: Callable[['CheckBox', 'PyStormDriver'], bool]

    def __init__(self, webdriver, parentElement, *args):
        super().__init__(webdriver, parentElement, *args)
        self.isCheckedFuncCB = defaultIsCheckedCB

    @retry(exceptions=(TimeoutException, UIException), delay=2, tries=2)
    def waitForChecked(self, isChecked=True):
        PrintMessage(f"Checkbox Waiter --- waiting for state to be: '{isChecked}'", inStepMessage=True)
        if self.isChecked == isChecked:
            return
        raise UIException(f"Failed to action checkbox, expected outcome isChecked:'{isChecked}'")

    def clear(self):
        self.element.clear()

    @retry(exceptions=(TimeoutException, UIException), delay=5, tries=5, backoff=2)
    def selectCheckBoxAndWait(self, isChecked=True, jsClick=False):
        PrintMessage(f"selectCheckBoxAndWait new state: '{isChecked}', actual: '{self.isChecked}', jsClick: '{jsClick}'", inStepMessage=True)
        if self.isChecked == isChecked:
            return

        self.click(jsClick=jsClick)
        self.waitForChecked(isChecked)

    @property
    def isChecked(self):
        """
        Used in radio buttons
        """
        # pylint: disable = too-many-function-args
        self.waitForElement()
        return self.isCheckedFuncCB(self, self.webdriver)

    @property
    def isInputDisabled(self):
        self.waitForElement()
        return bool(self.inputTypeElement.get_attribute('disabled'))

    @property
    def inputTypeElement(self) -> PyStormElement:
        """
        input type element for checkbox - it holds checked property
        Returns the input element that is either a preceding or following sibling of the current element.
        """
        return self.element.find_element(By.XPATH, ".//preceding-sibling::input | .//following-sibling::input")
