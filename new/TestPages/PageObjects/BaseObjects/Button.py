from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject


class Button(BaseTestObject):
    @property
    def isActive(self):
        """
        Some buttons when clicked, become active i.e. active class is added to element
        This property indicates if button was already clicked
        :return:
        """
        self.waitForElement()
        return 'active' in self.element.get_attribute('class')
