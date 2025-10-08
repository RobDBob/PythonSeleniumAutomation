import operator
from retry import retry
from selenium.common import exceptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.CustomExceptions import UIException
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.WebDriver import ExpectedConditions as EC


class DropdownListbox(BaseTestObject):
    """
    Working off listbox (aria type)
    Instantiated object does not need those two and safe coded to work without
    This way we can bypass init.
    """

    def __init__(self,
                 webdriver,
                 parentElement,
                 byType,
                 value,
                 optionsLocator=(By.CSS_SELECTOR, "div.item[role='option']"),
                 checkAriaState=True):
        super().__init__(webdriver, parentElement, byType, value)

        self.optionsLocator = optionsLocator
        self.wait = None

        # accounts for inconsistent dropdown implementations
        self.checkAriaState = checkAriaState

        # element's attribute indicating being selected
        self.selectedOptionAttribute = 'selected'

    def waitForDropdown(self):
        try:
            waitCondition = EC.visibility_of_element_located(self.element)
            WebDriverWait(self.parentElement, self.defaultWait).until(waitCondition)
        except TimeoutException:
            pass

    @retry(exceptions=UIException, delay=2, tries=2)
    def getOptionFromPartialText(self, optionPartialText):
        matchingOptions = [k for k in self.getAvailableOptionsAsText() if optionPartialText.lower() in k.lower()]
        if matchingOptions:
            return matchingOptions[0]
        raise UIException(f"Failed to find partial option match for: '{optionPartialText}'")

    def waitForOptions(self, expectedOptions):
        """
        This method waits for expected options to appear.
        """
        if type(expectedOptions) not in [tuple, list]:
            expectedOptions = [expectedOptions]
        for expectedOption in expectedOptions:
            waitCondition = EC.text_to_be_present_in_any_of_elements(self.optionsLocator, expectedOption)
            WebDriverWait(self.element, 60).until(waitCondition)

    @retry(exceptions=UIException, delay=2, tries=3)
    def getAvailableOptions(self, expectedOption=None):
        """
        Wait for option to be available before returning all options
        """

        if expectedOption:
            self.waitForOptions(expectedOption)

        return self.element.find_elements(*self.optionsLocator)

    def getAvailableOptionsAsText(self, expectedOption=None):
        """
        Function opens dropdown
        Reads available options
        Folds up dropdown and returns results
        """
        self.clickDropdown(True)
        try:
            options = self.getAvailableOptions(expectedOption)
            optionsText = [k.text for k in options]
        finally:
            self.clickDropdown(False)
        return optionsText

    def selectOptionFromPartialText(self, partialText):
        optionName = self.getOptionFromPartialText(partialText)
        self.selectOption(optionName)

    @retry(exceptions=(exceptions.StaleElementReferenceException, ValueError), delay=2, tries=3)
    def selectOption(self, optionToSelect: str, comparisonOperator: operator = operator.eq):
        """
        incoming option and list of available options are all in small case with whitespaces removed
        """
        PrintMessage(f"Selecting option of '{optionToSelect}'", inStepMessage=True)
        self.clickDropdown(True)

        allOptions = self.getAvailableOptions(optionToSelect)
        optionToSelectStandardized = optionToSelect.replace(' ', '').lower()
        for anOption in allOptions:
            anOptionText = anOption.text.replace(' ', '').lower()
            if comparisonOperator(anOptionText, optionToSelectStandardized):
                Button(self.webdriver, self.element, anOption).click()
                break

        if self.wait is not None:
            self.wait()

    @retry(exceptions=(exceptions.StaleElementReferenceException, ValueError), delay=2, tries=3)
    def selectOptionForLargeDropdown(self, optionToSelect: str):
        """
        Optimized to use JavaScript for faster selection in large dropdowns.
        """
        PrintMessage(f"Selecting option of '{optionToSelect}'", inStepMessage=True)

        # Use JavaScript to directly set the value and trigger the change event
        dropDownElement = self.element
        self.webdriver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            dropDownElement,
            optionToSelect
        )

        if self.wait is not None:
            self.wait()

    def clickDropdown(self, toExpand=True):
        self.waitForDropdown()
        self.scrollToElement()

        if self.checkAriaState:
            isExpanded = self.element.get_attribute("aria-expanded") == "true"

            if isExpanded != toExpand:
                self.click()

            waiter = EC.text_value_in_attribute_in_element(self.element, "aria-expanded", str(toExpand).lower())
            WebDriverWait(self.parentElement, 60).until(waiter)
        else:
            self.click()

    def selectedOptionLabel(self):
        return self.selectedOption

    @retry(exceptions=UIException, delay=2, tries=2)
    def waitForSelectedOption(self, expectedOptionText, comparisonOperator: operator = operator.eq):
        selectedOptionText = self.selectedOption
        if comparisonOperator(expectedOptionText, selectedOptionText):
            return
        raise UIException(f"Expected option '{expectedOptionText}' got instead '{selectedOptionText}'")

    @property
    def selectedOption(self):
        selectedOption = [k for k in self.getAvailableOptions() if k.get_attribute(self.selectedOptionAttribute)]
        if selectedOption:
            return selectedOption[0].text
        return ""
