from selenium.webdriver.common.by import By
from CommonCode.Driver.PyStormDriver import PyStormDriver
from CommonCode.Driver.PyStormElement import PyStormElement

CSS_CHECK_SUB_ELEMENT_LOCATOR = (By.XPATH, ".//span[@aria-hidden]")
CSS_CHECK_PSEUDO_ELEMENT = "::after"

# These callbacks are used to determine the state of various elements, such as checkboxes and inputs.


def defaultIsCheckedCB(element: PyStormElement, _):
    return bool(element.get_attribute("checked"))


def boldFontIsCheckedCB(element: PyStormElement, _):
    return element.find_element(By.XPATH, ".//span[contains(@class, 'label')]").get_attribute("style") == "font-weight: bold;"


def isPrecedingSiblingInputCheckedCB(element: PyStormElement, _):
    inputElement = element.find_element(By.XPATH, ".//preceding-sibling::input")
    return bool(inputElement.get_attribute('checked'))


def isFollowingSiblingInputCheckedCB(element: PyStormElement, _):
    inputElement = element.find_element(By.XPATH, ".//following-sibling::input")
    return bool(inputElement.get_attribute('checked'))


def isInputChildCheckedCB(element: PyStormElement, _):
    inputElement = element.find_element(By.XPATH, ".//input")
    return inputElement.is_selected()


def isCSSCheckedCB(element: PyStormElement, webdriver: PyStormDriver):
    from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
    jsScript = f"return window.getComputedStyle(arguments[0], '{CSS_CHECK_PSEUDO_ELEMENT}').getPropertyValue('content');"
    baseElement = BaseTestObject(webdriver, element, *CSS_CHECK_SUB_ELEMENT_LOCATOR)
    return webdriver.execute_script(jsScript, baseElement.element) != "none"


def defaultIsDisabledCB(element: PyStormElement, _):
    return bool(element.get_attribute('disabled'))


def isPrecedingSiblingInputDisabledCB(element: PyStormElement, _):
    inputElement = element.find_element(By.XPATH, ".//preceding-sibling::input")
    return bool(inputElement.get_attribute('disabled'))


def isInputChildDisabledCB(element: PyStormElement, _):
    inputElement = element.find_element(By.XPATH, ".//input")
    return bool(inputElement.get_attribute('disabled'))
