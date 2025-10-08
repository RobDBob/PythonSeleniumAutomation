from retry import retry
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.PageObjects.BaseObjects.EditField import EditField
from TestPages.WebDriver import ExpectedConditions as EC


class InputSwitcher(BaseTestObject):
    """
    Page object with single edit box & two switches (Pound & Percentage)
    """
    @retry(exceptions=TimeoutException, delay=3, tries=2)
    def insertPercentageValue(self, percentValue):
        self.percentageButton.click()
        waitCondition = EC.presence_of_element_located((By.XPATH, ".//span[@class='symbol' and text()='%']"))
        WebDriverWait(self.parentElement, 20).until(waitCondition)
        self.editBox.enterValue(percentValue)

    @retry(exceptions=TimeoutException, delay=3, tries=2)
    def insertPoundValue(self, poundValue):
        self.poundButton.click()
        waitCondition = EC.presence_of_element_located((By.XPATH, ".//span[@id and text()='£']"))
        WebDriverWait(self.parentElement, 20).until(waitCondition)
        self.editBox.enterValue(poundValue)

    @property
    def percentageButton(self):
        return Button(self.webdriver, self.element, By.XPATH, ".//span[@title='%']")

    @property
    def poundButton(self):
        return Button(self.webdriver, self.element, By.XPATH, ".//span[@title='£']")

    @property
    def editBox(self):
        return EditField(self.webdriver, self.element, By.XPATH, ".//input[@inputmode='numeric']")
