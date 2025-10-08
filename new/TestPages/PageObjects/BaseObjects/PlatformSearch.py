from retry import retry
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages import PageEnums
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.PageObjects.BaseObjects.EditField import EditField
from TestPages.PageObjects.BaseObjects.Labels import Label
from TestPages.WebDriver import ExpectedConditions as EC


class PlatformSearch(BaseTestObject):
    DEFAULT_OPTIONS_LOCATOR = (By.XPATH, ".//ul[@id='smart-search']/li/div")
    SEARCH_RESULTS_HEADING_OPTIONS_LOCATOR = (By.XPATH, ".//div[contains(@id,'search-result')]/b")
    SEARCH_RESULTS_OPTIONS_LOCATOR = (By.XPATH, ".//ul[@class='list-view']/li/div//span")

    def waitForTopSearchOptions(self, optionType, expectedOptions):
        """
        This method waits for expected options to appear for the default, heading and results of the advanced search bar
        """
        match optionType:
            case PageEnums.Default:
                optionsLocator = self.DEFAULT_OPTIONS_LOCATOR
            case PageEnums.Heading:
                optionsLocator = self.SEARCH_RESULTS_HEADING_OPTIONS_LOCATOR
            case PageEnums.Results:
                optionsLocator = self.SEARCH_RESULTS_OPTIONS_LOCATOR

        if type(expectedOptions) not in [tuple, list]:
            expectedOptions = [expectedOptions]
        for expectedOption in expectedOptions:
            waitCondition = EC.text_to_be_present_in_any_of_elements(optionsLocator, expectedOption)
            WebDriverWait(self.element, 60).until(waitCondition)

    @retry(exceptions=TimeoutException, delay=2, tries=3)
    def searchAndSelect(self, textToSearch, textToSelect=None):
        PrintMessage('Searching using top search function', inStepMessage=True)
        if not textToSelect:
            textToSelect = textToSearch

        self.enterValue(textToSearch)
        self.searchButton.click()
        self.clickOnSearchResult(textToSelect)

    @retry(exceptions=TimeoutException, delay=2, tries=3)
    def enterValue(self, value):
        self.topSearchBoxField.clear_using_backspace(self.topSearchBoxField.value)
        self.topSearchBoxField.enterValue(value)

        waitCondition = EC.text_value_in_attribute_in_element(self.topSearchBoxField.element, "value", value)
        WebDriverWait(self.parentElement, 15).until(waitCondition)

    def clickOnSearchResult(self, textToSelect):
        PrintMessage(f"Attempting to select Option: '{textToSelect}'", inStepMessage=True)

        searchResult = Button(self.webdriver, self.element, By.XPATH, f".//ul[@class='list-view']//li//div//button//span[contains(text(), '{textToSelect}')]")
        viewButton = Button(self.webdriver, self.element, By.XPATH, "//button[text()='View client']")
        searchResult.click()
        viewButton.click()

        waitCondition = EC.text_value_in_attribute_in_element(self.topSearchBoxField.element, "value", textToSelect)
        WebDriverWait(self.parentElement, 20).until_not(waitCondition)

    @property
    def searchBoxPlaceholderLabel(self):
        return Label(self.webdriver, self.element, By.XPATH, ".//input[@class='search-input']")

    @property
    def searchButton(self):
        return Button(self.webdriver, self.element, By.XPATH, ".//button[@class='search-icon']")

    @property
    def advancedSearchHyperLink(self):
        return Button(self.webdriver, self.element, By.XPATH, ".//button[@class='ist-advanced-toggle']")

    @property
    def topSearchBoxField(self):
        return EditField(self.webdriver, self.element, By.XPATH, ".//input[@id='Search bar']")
