import os
from urllib.parse import parse_qs, urlparse
from retry import retry
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from CommonCode.API.Wrap.PlatformRequestsHelper import PlatformRequestsHelper
from CommonCode.CustomExceptions import FileNotReadyException
from CommonCode.Driver.PyStormDriver import PyStormDriver
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import TestContext
from CommonCode.TestHelpers import FileHelper
from CommonCode.TestHelpers.StringMethods import getUniqueAlphaNumericString
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.WebDriver import ExpectedConditions as EC


class DocumentDownloader:
    DOWNLOAD_ELEMENT_LOCATOR = (By.CSS_SELECTOR, "[class*='download-button']")
    SPINNER_LOCATOR = "span[contains(@class, 'lds-dual-ring')]"
    SPINNER_CSS_LOCATOR = (By.CSS_SELECTOR, "[class*='lds-dual-ring']")
    HREF_LOCATOR = (By.XPATH, "//a[contains(@href, 'wpadviser')]")
    HREF_PARAM_FILE_NAME = "fileName"
    HREF_PARAM_TASK_REQUEST_ID = "taskRequestId"
    SPINNER_TIME_OUT = 480

    def __init__(self, webdriver, testContext: TestContext):
        self.webdriver: PyStormDriver = webdriver
        self.testContext: TestContext = testContext
        self.downloadFolder = self.testContext.testDownloadFolder

        os.makedirs(self.downloadFolder, exist_ok=True)

    def _triggerDocGenerationFromHREFAttribute(self):
        downloadElements = self.webdriver.find_elements(*self.DOWNLOAD_ELEMENT_LOCATOR)
        downloadElementsWithoutHref = [k for k in downloadElements if not k.get_attribute("href")]

        for elementWithoutHref in downloadElementsWithoutHref:
            elementWithoutHref.click()

            waitCondition = EC.presence_of_element_located(self.SPINNER_CSS_LOCATOR)
            WebDriverWait(self.webdriver, self.SPINNER_TIME_OUT).until_not(waitCondition)

    def _getParameterValueHref(self, href, parameterName):
        """
        Skips white spapces in file name
        """
        if not href:
            assert href, "_getParameterValueHref > at this stage expected to get href"
            return None

        parsedURL = urlparse(href)
        parameterValue = next(iter(parse_qs(parsedURL.query).get(parameterName, [])), "")
        if not parameterValue:
            PrintMessage(f"Failed to extract parameter '{parameterName}' from href '{href}'")

        if parameterName == self.HREF_PARAM_FILE_NAME:
            # remove white spaces
            return "".join(parameterValue.split())
        return parameterValue

    def _checkExistingFilesPriorDownload(self, downloadFolder):
        """
        default name for downloaded file is LoadDocStore.PDF
        Check if this file exists, if it is rename it
        all is compared in lower case
        """
        potentialLeftOverFiles = ["loaddocstore.pdf"]

        existingFiles = os.listdir(downloadFolder)
        existingFiles = [k.lower() for k in existingFiles]
        PrintMessage(f"Existing files: {existingFiles}")

        for leftOverFile in potentialLeftOverFiles:
            if leftOverFile in existingFiles:
                os.rename(os.path.join(downloadFolder, leftOverFile), os.path.join(downloadFolder, f"{getUniqueAlphaNumericString()}_{leftOverFile}"))
        return os.listdir(downloadFolder)

    def _getAllHrefs(self):
        clickableDownloads = self.webdriver.find_elements(*self.HREF_LOCATOR)
        return [k.get_attribute('href') for k in clickableDownloads]

    def cleanDownloadFolder(self):
        existingFiles = os.listdir(self.downloadFolder)
        PrintMessage(f"Deleting any existing files: {existingFiles}")
        for currentFile in existingFiles:
            filePath = os.path.join(self.downloadFolder, currentFile)
            os.remove(filePath)
            FileHelper.waitForFileToBeRemoved(filePath)
        PrintMessage(f"Download folder '{self.downloadFolder}' contents: '{os.listdir(self.downloadFolder)}'")

    @retry(exceptions=(TimeoutException, StaleElementReferenceException), tries=3)
    def waitForDocumentGenerationToFinish(self):
        PrintMessage("downloadDocuments > _waitForDocumentGenerationToFinish")
        waitcondition = EC.visibility_of_just_one_element_located(self.SPINNER_CSS_LOCATOR)
        try:
            WebDriverWait(self.webdriver, 80).until(waitcondition, "Expecting spinner to appear")
        except TimeoutException:
            pass
        waitcondition = EC.visibility_of_any_elements_located(self.SPINNER_CSS_LOCATOR)
        WebDriverWait(self.webdriver, self.SPINNER_TIME_OUT).until_not(waitcondition, "Expecting spinner to cease appearing")

    def downloadAllDocumentsViaUI(self):
        self._triggerDocGenerationFromHREFAttribute()
        filePaths = []

        for href in self._getAllHrefs():
            urlFileName = self._getParameterValueHref(href, self.HREF_PARAM_FILE_NAME)
            taskRequestId = self._getParameterValueHref(href, self.HREF_PARAM_TASK_REQUEST_ID)
            existingFiles = self._checkExistingFilesPriorDownload(self.downloadFolder)

            clickableDownload = self.webdriver.find_element(By.XPATH, f"//a[contains(@href, '{taskRequestId}')]")
            clickableDownload.click()

            downloadedFilePath = FileHelper.waitForNewFile(existingFiles, self.downloadFolder)
            savedFilePath = os.path.join(self.downloadFolder, urlFileName)
            os.rename(downloadedFilePath, savedFilePath)
            filePaths.append(savedFilePath)
        return filePaths

    @retry(exceptions=FileNotReadyException, delay=10, tries=2)
    def downloadDocument(self, baseTestObject: BaseTestObject, newFileName):
        """
        Method checks for existing files first before clicking on download UI element
        """
        existingFiles = self._checkExistingFilesPriorDownload(self.downloadFolder)
        baseTestObject.click()
        downloadedFilePath = FileHelper.waitForNewFile(existingFiles, self.downloadFolder)
        downloadedFileNewName = os.path.join(self.downloadFolder, newFileName)
        PrintMessage(f"Renamed downloaded file: '{downloadedFilePath}' to '{downloadedFileNewName}'")
        os.rename(downloadedFilePath, downloadedFileNewName)
        return downloadedFileNewName

    def downloadAllDocumentsViaAPI(self):
        """
        Method works out how many documents there are by searching for [class*='download-button']
        Once all are identified, it'll trigger download for all of them
        Download file name is extracted from hyperlink if it has 'fileName' property otherwise generic name is used

        Caveat: if more than one document is missing fileName the result files gets overwritten
        Downloaded files are saved to /downloads/<testId>/ folder

        Caveat2: Method still triggers document download via UI elements and so windows form to save doc is shown in headfull
        """
        self._triggerDocGenerationFromHREFAttribute()
        filePaths = []

        platformRequests = PlatformRequestsHelper(self.webdriver.apiSessionHeaders, self.testContext)
        for href in self._getAllHrefs():
            fileName = self._getParameterValueHref(href, self.HREF_PARAM_FILE_NAME)
            destFilePath = os.path.join(self.downloadFolder, fileName)
            platformRequests.downloadFile(href, destFilePath)
            filePaths.append(destFilePath)
        return filePaths

    @retry(exceptions=TimeoutException, delay=30, tries=6)
    def waitForDocumentsToBeGenerated(self, documentNames: list):
        """
        waits until all mentioned documents are generated and ready to be downloaded
        """
        documentNames.reverse()
        for documentName in documentNames:
            PrintMessage(f"Waiting for document: '{documentName}' generation to complete")
            locator = f"//span[text()='{documentName}']//following-sibling::{self.SPINNER_LOCATOR}"
            waitcondition = EC.presence_of_element_located((By.XPATH, locator))
            WebDriverWait(self.webdriver, self.SPINNER_TIME_OUT).until_not(waitcondition)

    def downloadDocumentsFromURL(self, url, fileName):
        destFilePath = os.path.join(self.downloadFolder, fileName)
        platformRequests = PlatformRequestsHelper(self.webdriver.apiSessionHeaders, self.testContext)
        platformRequests.downloadFile(url, destFilePath)
