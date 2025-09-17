from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from CommonCode.CustomExceptions import UIException
from CommonCode.TestExecute.Logging import PrintMessage


def hoverAndHold(driver: WebDriver, element: WebElement):
    """
    method to move the mouse pointer to an element, click and Hold
    """
    try:
        hoverAndHold = ActionChains(driver).move_to_element(element).click_and_hold()
        hoverAndHold.perform()
        PrintMessage("Mouse action performed succesfully")
    except UIException as e:
        PrintMessage(f"Error while performing mouse action: {e}")
