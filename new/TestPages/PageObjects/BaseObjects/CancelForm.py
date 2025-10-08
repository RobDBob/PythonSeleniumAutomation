from selenium.webdriver.common.by import By
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.PageObjects.BaseObjects.Labels import Label


class CancelForm(BaseTestObject):
    @property
    def pageTitle(self):
        return Label(self.webdriver, self.element, By.XPATH, ".//h1")

    @property
    def yesButton(self):
        return Button(self.webdriver, self.element, By.XPATH, ".//button[contains(@class, 'btn') and text()='Yes']")

    @property
    def noButton(self):
        return Button(self.webdriver, self.element, By.XPATH, ".//button[contains(@class, 'btn') and text()='No']")
