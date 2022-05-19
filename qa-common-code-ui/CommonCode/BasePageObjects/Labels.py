from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject
from CommonCode.TestExecute.Logging import PrintMessage


class Label(BaseTestObject):
    """
    Simple web element.
    """
    def click(self):
        self.element.click()
        PrintMessage('Label clicked.')

    @property
    def text(self):
        return self.element.text

    @property
    def inner_text(self):
        return self.element.get_attribute('innerText')

    @property
    def value_text(self):
        """
        The actual text might be something along those lines: u'EOG Resources (5,471)'
        We are interested only in 'EOG Resources'
        :return:
        """
        return self.element.get_attribute('value')
