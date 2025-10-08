import operator
from typing import Callable
from retry import retry
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.CustomExceptions import UIException
from CommonCode.Driver.PyStormDriver import PyStormDriver
from CommonCode.Driver.PyStormElement import PyStormElement
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.StateCallbacks import defaultIsDisabledCB
from TestPages.WebDriver import ExpectedConditions as EC


class BaseTestObject:
    webdriver = None
    _element: PyStormElement = None
    isDisabledFuncCB: Callable[['BaseTestObject'], bool]

    def __init__(self, webdriver, parentElement, *args):
        """
        :param parentElement:
        :param byType:
        :param value:

        See if this can be rewritten in more pythonic way, replace args with class methods
        https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-implement-multiple-constructors
        """
        self.webdriver: PyStormDriver = webdriver
        self.parentElement = parentElement

        if len(args) == 1 and isinstance(args[0], PyStormElement):
            self.element = args[0]
        elif len(args) == 2:
            self.findByType = args[0]
            self.findByValue = args[1]
        else:
            raise UIException(f"Wrong arguments: '{list(args)}'")

        self.defaultWait = 60
        self.isDisabledFuncCB = defaultIsDisabledCB

    @classmethod
    def createFromElement(cls, parentElement, incElement: PyStormElement):
        baseObject = BaseTestObject(parentElement, incElement.findByType, incElement.findByValue)
        baseObject.element = incElement
        return baseObject

    def _getLocator(self):
        if self._element:
            return self._element
        return (self.findByType, self.findByValue)

    def _waitForElement(self, expectedCondition, *args, **kwargs):
        waiterCriteria = expectedCondition(self._getLocator(), *args)
        WebDriverWait(self.parentElement, self.defaultWait).until(waiterCriteria, message=kwargs.get("message"))

    def _findElements(self) -> list[PyStormElement]:
        return [k for k in self.parentElement.find_elements(self.findByType, self.findByValue) if k.is_displayed]

    def waitForElement(self):
        """
        Waiting for element to be present before allowing to continue.
        If this fails after self.defaultWait we let it go as subsequent code might handle missing element case.

        15/10/24 RobD: counternote: allowing it to fail hides issues with locators and causes test framework to run exceedingly long,
         - removed try - except - pass
        This needs further considerations on how to deal with these issues
        :return:
        """
        visibleElement = EC.presence_of_element_located(self._getLocator())
        WebDriverWait(self.parentElement, self.defaultWait).until(visibleElement, f"Failed presence_of_element_located: {self._getLocator()}")

        visibleElement = EC.visibility_of_element_located(self._getLocator())
        WebDriverWait(self.parentElement, self.defaultWait).until(visibleElement, f"Failed visibility_of_element_located: {self._getLocator()}")

    def waitForElementToCeaseExist(self):
        invisibleElement = EC.invisibility_of_element_located(self._getLocator())
        WebDriverWait(self.parentElement, self.defaultWait).until(invisibleElement)

    def waitForTextAsNumber(self, expectedNumericValue: float, comparisonOperator: operator = operator.eq):
        message = f"Waiting For Text > '{expectedNumericValue}'"
        PrintMessage(message, inStepMessage=True)
        try:
            self._waitForElement(EC.float_to_be_present_in_element, expectedNumericValue, comparisonOperator, message=message)
        except TimeoutException as exc:
            raise TimeoutException(f"Expected '{expectedNumericValue}' and instead got '{self.text}'") from exc

    def waitForText(self, expectedText: str, comparisonOperator: operator = operator.contains):
        message = f"Waiting For Text > '{expectedText}'"
        PrintMessage(message, inStepMessage=True)
        try:
            self._waitForElement(EC.text_to_be_present_in_element, str(expectedText), comparisonOperator, message=message)
        except TimeoutException as exc:
            raise TimeoutException(f"Expected '{expectedText}' and instead got '{self.text}'") from exc

    def waitForValue(self, expectedValue, comparisonOperator: operator = operator.contains):
        self.waitForTextInAttribute(expectedValue, "value", comparisonOperator)

    def waitForTextInAttribute(self, expectedText, attributeName="value", comparisonOperator: operator = operator.contains):
        message = f"Waiting For value > '{expectedText}' in attribute: '{attributeName}'"
        PrintMessage(message, inStepMessage=True)
        self._waitForElement(EC.text_value_in_attribute_in_element, attributeName, expectedText, comparisonOperator, message=message)

    # pylint: disable=invalid-name
    def get_attribute(self, value):
        return self.element.get_attribute(value)

    def find_elements(self, by, value) -> list[PyStormElement]:
        return self.element.find_elements(by, value)

    def find_element(self, by, value) -> PyStormElement:
        return self.element.find_element(by, value)

    # ---=== Additional functionality shared between UI elements ---===

    def exists(self):
        """
        Test method checking if UI element was found
        Rather than failing if does not exist outright, framework will wait default timeout before failing
        :return:
        """
        return self.element is not None

    def scrollToElement(self, adjustX=0, adjustY=0):
        # parent.execute_script("arguments[0].scrollIntoView(true)", self.element)
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(self.webdriver).scroll_to_element(self.element).scroll_by_amount(adjustX, adjustY).perform()

    def scrollToEndOfElement(self):
        """
        This logic will work as a workaround for those element which are hidden due to page resolution change
        And to scroll horizontally till the end of the element.
        """
        self.webdriver.execute_script("arguments[0].scrollIntoView({inline: 'end'})", self.element)

    @retry(exceptions=(ElementClickInterceptedException, WebDriverException, UIException, StaleElementReferenceException), tries=3)
    def click(self, skipScrollTo=False, jsClick=False):
        waiterCriteria = EC.element_to_be_clickable(self.element)
        WebDriverWait(self.parentElement, 15).until(waiterCriteria)

        skipScrollTo = self.element.tag_name in ["option"] or skipScrollTo

        if jsClick:
            self.jsClick(skipScrollTo)
            return

        if not skipScrollTo:
            self.scrollToElement()

        self.element.click()

    @retry(exceptions=(ElementClickInterceptedException, WebDriverException, UIException, StaleElementReferenceException), tries=3)
    def jsClick(self, skipScrollTo=False):
        """This works under assumption that parentElement is the pystorm webdriver"""

        waiterCriteria = EC.element_to_be_clickable(self.element)
        WebDriverWait(self.parentElement, 15).until(waiterCriteria)

        if not skipScrollTo:
            self.scrollToElement()
        self.webdriver.execute_script("arguments[0].click();", self.element)

    @property
    def element(self) -> PyStormElement:
        """
        Added this property to find element each time it is called, due to web browser refreshes on re-size
        :return:
        """
        if self._element:
            return self._element

        self.waitForElement()

        foundElements = self._findElements()

        if len(foundElements) > 0:
            foundElements[0].findByType = self.findByType
            foundElements[0].findByValue = self.findByValue
            return foundElements[0]
        return None

    @element.setter
    def element(self, value):
        self._element = value

    @property
    def textOnly(self):
        return self.element.get_attribute('textContent').strip()

    @property
    def text(self):
        return self.element.text

    @property
    def innerHTMLText(self):
        return self.element.get_attribute('innerHTML').strip()

    @property
    def value(self):
        return self.element.get_attribute("value")

    @property
    def innerText(self):
        return self.element.get_attribute("innerText")

    @property
    def placeholderText(self):
        return self.element.get_attribute("placeholder")

    @property
    def isDisabled(self):
        self.waitForElement()
        return self.isDisabledFuncCB(self, self.webdriver)

    @property
    def spotCheckExists(self):
        """
        Quick check for element being available
        This bypasses waitForElement and so use with caution
        """
        if self._element:
            return True
        return len(self._findElements()) > 0

    @property
    def spotCheckHidden(self):
        """
        Quick check for element being visible
        This bypasses waitForElement and so use with caution
        """
        if self._element:
            return self._element.isHidden
        elements = self._findElements()
        if elements:
            element = elements[0]
            return element.isHidden
        return True

    @property
    def spotCheckDisplayed(self):
        """
        Quick check for element being displayed (visible in DOM and not hidden).
        This bypasses waitForElement and so use with caution.
        """
        if self._element:
            return self._element.is_displayed()
        elements = self._findElements()
        if elements:
            return elements[0].is_displayed()
        return False

    @property
    def isHidden(self):
        return self.element.isHidden

    @property
    def isAriaExpanded(self):
        return self.element.get_attribute("aria-expanded") == "true"

    @property
    def isAreaSelected(self):
        return self.element.get_attribute("aria-selected") == "true"

    @property
    def isElementInViewport(self):
        # unused but might come handy
        # for future ref: https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect
        return self.webdriver.execute_script("var elem = arguments[0],                 "
                                             "  box = elem.getBoundingClientRect(),    "
                                             "  cx = box.left + box.width / 2,         "
                                             "  cy = box.top + box.height / 2,         "
                                             "  e = document.elementFromPoint(cx, cy); "
                                             "for (; e; e = e.parentElement) {         "
                                             "  if (e === elem)                        "
                                             "    return true;                         "
                                             "}                                        "
                                             "return false;                            ", self.element)

    @property
    def elementAttributes(self):
        if not self.webdriver:
            return ""
        return self.webdriver.execute_script("""var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index)
                                             { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;""", self.element)

    @property
    def convertCurrencyInStringFormatToFloat(self):
        try:
            return float(self.text.replace('£', '').replace(',', ''))
        except ValueError:
            PrintMessage(f"Failed to convert '{self.text}' to Float value!", inStepMessage=True)
            return self.text
