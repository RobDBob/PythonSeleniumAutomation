from CommonCode.Enums_Utils import LoggingLevel
from CommonCode.TestExecute.Logging import PrintMessage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from CommonCode.WebDriver import ExpectedConditions


class BaseTestObject(object):
    def __init__(self, parent_web_element, by_type, value, index=0):
        """
        :param parent_web_element:
        :param by_type:
        :param value:
        :param index:
        """
        self.parent_web_element = parent_web_element
        self.element_by_type = by_type
        self.element_value = value
        self.element_index = index

        self.wait_for_element()

    def wait_for_element(self):
        """
        Waiting for element to be present before allowing to continue.
        If this fails after 30 we let it go as subsequent code might handle missing element case.
        :return:
        """
        try:
            visible_element = ExpectedConditions.presence_of_element_located(self.element)
            WebDriverWait(self.parent_web_element, 10).until(visible_element)
        except TimeoutException:
            PrintMessage("Failed presence_of_element_located wait in BaseTestObject.wait_for_element.",
                         LoggingLevel.warning)
            PrintMessage(f"by:{self.element_by_type}, value:{self.element_value}, index:{self.element_index})")
            pass

    def get_attribute(self, value):
        return self.element.get_attribute(value)

    def find_elements(self, by, value):
        return self.element.find_elements(by, value)

    def find_element(self, by, value, index=0):
        return self.element.find_element(by, value, index)

    # ---=== Additional functionality shared between UI elements ---===

    def exists(self):
        """
        Test method checking if UI element was found
        :return:
        """
        return self.element is not None

    def scroll_to_element(self):
        if isinstance(self.parent_web_element, WebDriver):
            self.parent_web_element.execute_script("arguments[0].scrollIntoView(true)", self.element)

    @property
    def element(self):
        """
        Added this property to find element each time it is called, due to web browser refreshes on re-size
        :return:
        """
        return self.parent_web_element.find_element(self.element_by_type, self.element_value, self.element_index)
