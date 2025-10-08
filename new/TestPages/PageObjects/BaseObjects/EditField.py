import time
from retry import retry
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from CommonCode.CustomExceptions import UIException
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject


# pylint: disable=invalid-name
class EditField(BaseTestObject):
    @retry(exceptions=UIException, delay=1, tries=2)
    def forceClearValue(self):
        self.clear()

        if self.value == "":
            return
        raise UIException("Value not cleared!")

    def clear(self):
        self.element.clear()

    @retry(exceptions=UIException, delay=2, tries=5)
    def clearEnterValue(self, value):
        PrintMessage(f"EditField > clearEnterValue Typing in: '{value}'.", inStepMessage=True)
        self.click()
        ActionChains(self.webdriver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        self.element.send_keys(Keys.DELETE)

        if self.text:
            raise UIException()

        self.element.send_keys(value)

    def enterValueAndWait(self, value):
        self.enterValue(str(value))
        self.waitForValue(str(value))

    def enterValue(self, value, forceClearValue=False):
        PrintMessage(f"EditField > enterValue Typing in: '{value}'.", inStepMessage=True)
        self.click()
        self.element.clear()

        if forceClearValue:
            self.forceClearValue()

        self.element.send_keys(value)
        self.element.send_keys(Keys.ENTER)

    def send_keys(self, value, clear=True):
        PrintMessage(f"EditField > send_keys Typing in: '{value}'.", inStepMessage=True)
        if clear:
            self.clear()
        self.element.send_keys(value)

    def send_keys_slowly(self, value, clear=True):
        PrintMessage(f"EditField > send_keys_slowly Typing in: '{value}'.", inStepMessage=True)
        self.scrollToElement()
        if clear:
            self.clear()
        for character in value:
            self.element.send_keys(character)
            time.sleep(0.05)

    def clear_using_backspace(self, value):
        PrintMessage(f"EditField > clear_using_backspace Typing in: '{value}'.", inStepMessage=True)
        for _ in range(0, len(value) + 1):
            self.element.send_keys(Keys.BACK_SPACE)

    def clearAndAddCharacters(self, numberOfChar, charToAdd=None):
        """
        This code works if specific consecutive characters from end of string
        are required to be replaced or removed
        """
        PrintMessage(f"EditField > clearAndAddCharacters Typing in: '{charToAdd}'.", inStepMessage=True)
        if charToAdd is None:
            for _ in range(0, numberOfChar):
                self.element.send_keys(Keys.BACK_SPACE)
                time.sleep(0.05)
            PrintMessage(f"Number of character as '{numberOfChar} removed", inStepMessage=True)
        else:
            for _ in range(0, numberOfChar):
                self.element.send_keys(Keys.BACK_SPACE)
            self.element.send_keys(charToAdd)
            self.element.send_keys(Keys.ENTER)
            PrintMessage(f"Number of character as '{numberOfChar}' removed and '{charToAdd}' entered.", inStepMessage=True)

    @property
    def borderColor(self):
        return self.element.value_of_css_property("border-color")
