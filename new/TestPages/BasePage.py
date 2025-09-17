import operator
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.Driver.PyStormAlert import PyStormAlert
from CommonCode.Driver.PyStormDriver import PyStormDriver
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context, TestContext
from CommonCode.TestHelpers.BrowserHelper import BrowserHelper
from TestPages.WebDriver import ExpectedConditions as EC


class BasePage:
    SPINNER_TIME_OUT = 360
    LOAD_ON_CREATE = True

    def __init__(self, webdriver: PyStormDriver):
        self.webdriver: PyStormDriver = webdriver
        self.testContext: TestContext = Test_Context
        self.browserHelper: BrowserHelper = BrowserHelper(self.webdriver, self.testContext)

        if self.LOAD_ON_CREATE:
            self.load()

    def navigate(self):
        return

    def wait(self):
        return

    def waitSpinner(self):
        spinnerTimeOut = 140

        waitCondition = EC.visibility_of_element_located((By.XPATH, "//div[@class='spinner-inner']"))
        try:
            WebDriverWait(self.webdriver, 1).until(waitCondition)
        except TimeoutException:
            pass
        WebDriverWait(self.webdriver, spinnerTimeOut).until_not(waitCondition, f"Waited {spinnerTimeOut}s for spinner to finish.")

    def load(self, refresh=False):
        if refresh:
            PrintMessage('Refreshing...')
            self.webdriver.refresh()
        PrintMessage(f"LOADING >> {type(self).__name__}")
        self.navigate()
        self.wait()

    def reload(self):
        self.webdriver.refresh()
        self.wait()

    def getAlert(self) -> PyStormAlert:
        try:
            alert: PyStormAlert = self.webdriver.switch_to.alert
            return alert
        except NoAlertPresentException:
            return False

    def switchToAlertAndAccept(self):
        alert = self.waitForAlert()
        alert.accept()

    def waitForAlert(self, expectedText=None, comparisonOperator: operator = operator.eq):
        waitCondition = EC.alert_is_present()
        WebDriverWait(self.webdriver, 15).until(waitCondition)

        alert: PyStormAlert = self.getAlert()
        if alert and expectedText:
            alert.waitForText(expectedText, comparisonOperator)
        return alert

    def getInlineErrorMessage(self):
        errorMessageLocator = (By.XPATH, "//p[@class='error mb-0']")
        valueWaiter = EC.visibility_of_all_elements_located(errorMessageLocator)
        WebDriverWait(self.webdriver, 60).until(valueWaiter)
        errorMessage = self.webdriver.find_elements(*errorMessageLocator)
        return [k.text for k in errorMessage]

    def getProcessErrorMessage(self):
        errorMassageLocator = (By.XPATH, "//p[@class='error-message undefined']")
        valueWaiter = EC.visibility_of_all_elements_located(errorMassageLocator)
        WebDriverWait(self.webdriver, 60).until(valueWaiter)
        errorMessage = self.webdriver.find_elements(*errorMassageLocator)
        return [k.text for k in errorMessage]

    def waitForErrorMessage(self, locator, expectedErrorMessage):
        if expectedErrorMessage:
            waitCondition = EC.text_to_be_present_in_any_of_elements((locator), expectedErrorMessage)
            WebDriverWait(self.webdriver, 60).until(waitCondition)
        else:
            waitCondition = EC.text_to_be_present_in_any_of_elements((locator), "")
            WebDriverWait(self.webdriver, 60).until_not(waitCondition)
