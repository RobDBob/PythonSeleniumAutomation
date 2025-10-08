from retry import retry
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.PageObjects.BaseObjects.EditField import EditField
from TestPages.PageObjects.BaseObjects.Labels import Label
from TestPages.WebDriver import ExpectedConditions as EC


class SmartSearchEdit(BaseTestObject):
    searchResultToSelectLocator = (By.XPATH, ".//button[text()='{0}']")
    searchFirstResultLocator = (By.XPATH, "//ul[not(contains(@style,'display: none;'))]/li[@class='ui-menu-item']/div[text()]")
    isEditBoxClearedAfterSelection = False

    @retry(exceptions=ElementClickInterceptedException, tries=5)
    def _clickOnFirstResult(self):
        waitCondition = EC.presence_of_element_located(self.searchFirstResultLocator)
        WebDriverWait(self.parentElement, 30).until(waitCondition)
        resultButton = Button(self.webdriver, self.parentElement, *self.searchFirstResultLocator)
        resultText = resultButton.text

        # Odd case where results are rendered under search box
        # But within DOM are located at the bottom of page
        self.scrollToElement(adjustY=50)
        if resultText == "No results found":
            PrintMessage("SmartSearchEdit > clickOnFirstResult> ERROR: No search results found, returning empty string", inStepMessage=True)
        else:
            resultButton.click(skipScrollTo=True)

        return resultText

    def _clickOnSearchResult(self, textToSelect):
        """
        Method assumes that once record is selected, it'll get removed from search box
        This assumption is used in self.isEditBoxClearedAfterSelection
        """
        PrintMessage(f"Attempting to select Option: '{textToSelect}'", inStepMessage=True)
        byType, byValue = self.searchResultToSelectLocator

        waitCondition = EC.presence_of_element_located((byType, byValue.format(textToSelect)))
        WebDriverWait(self.parentElement, 30).until(waitCondition)

        Button(self.webdriver, self.parentElement, byType, byValue.format(textToSelect)).click()

        if self.isEditBoxClearedAfterSelection:
            # expectance is, search term is removed from edit box after selection
            waitCondition = EC.text_value_in_attribute_in_element(self.input.element, "value", textToSelect)
            WebDriverWait(self.parentElement, 20).until_not(waitCondition)

    @retry(exceptions=TimeoutException, tries=5)
    def searchAndSelectFirstMatch(self, textToSearch):
        # In repeated uses need to slow down between searching & selecting, then searching again
        waitCondition = EC.text_to_be_present_in_element(self.input.element, "")
        WebDriverWait(self.parentElement, 2).until(waitCondition)

        self.enterValue(textToSearch)
        return self._clickOnFirstResult()

    @retry(exceptions=TimeoutException, tries=5)
    def searchAndSelect(self, textToSearch, textToSelect=None):
        if not textToSelect:
            textToSelect = textToSearch

        self.enterValue(textToSearch)
        self._clickOnSearchResult(textToSelect)

    def clickSearchAndSelect(self):
        self.click()

    # pylint: disable=invalid-name
    @retry(exceptions=TimeoutException, delay=2, tries=3)
    def enterValue(self, value):
        self.input.enterValue(value)

    @property
    def placeholderText(self):
        inputTypeElement = self.element.find_element(By.XPATH, ".//preceding-sibling::input")
        return inputTypeElement.get_attribute("placeholder")

    @property
    def text(self):
        return self.element.get_attribute('innerHTML').strip()

    @property
    def title(self):
        return Label(self.webdriver, self.element, By.XPATH, ".//label[@for]")

    @property
    def input(self):
        return EditField(self.webdriver, self.element, By.XPATH, ".//input")
