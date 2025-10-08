from selenium.webdriver.common.by import By
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.PageObjects.BaseObjects.Labels import Label


class HintDialog(BaseTestObject):
    def checkHintDialog(self, title, content):
        PrintMessage("Checking hint dialog...")
        self.pageTipsDialog.waitForElement()
        self.title.waitForText(title)
        self.content.waitForText(content)
        self.nextButton.waitForElement()
        self.dismissButton.waitForElement()
        PrintMessage("Hint dialog is displayed correctly.")

    @property
    def pageTipsDialog(self):
        return HintDialog(self.webdriver, self.element, By.XPATH, "//div[@role='dialog']")

    @property
    def nextButton(self):
        return Button(self.webdriver, self.element, By.XPATH, "//button[@class='btn cm-next-button']")

    @property
    def dismissButton(self):
        return Button(self.webdriver, self.parentElement, By.CSS_SELECTOR, "button[class='cm-close-button']")

    @property
    def title(self):
        return Label(self.webdriver, self.element, By.ID, "cmTitle")

    @property
    def content(self):
        return Label(self.webdriver, self.element, By.ID, "cmContent")

    @property
    def gotItButton(self):
        return Button(self.webdriver, self.element, By.XPATH, "//span[text()='Got it']//parent::button")
