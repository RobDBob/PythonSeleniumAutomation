import json
import os
from selenium.webdriver.remote.webdriver import WebDriver
from CommonCode.HelperFunctions import tryExecute
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.Screenshot import Screenshot
from CommonCode.TestExecute.TestContext import TestContext
from CommonCode.TestHelpers import FileHelper
from CommonCode.TestHelpers.DateMethods import getTimeStamp
from CommonCode.TestHelpers.StringMethods import getUniqueAlphaNumericString


class BrowserHelper:
    screenshotFolderName = "screenshots"
    evidenceFolderName = "testEvidence"

    def __init__(self, webdriver, testContext):
        self.webdriver: WebDriver = webdriver
        self.testContext: TestContext = testContext

    def _removeExistingScreenshot(self, filePath):
        if os.path.isfile(filePath):
            try:
                os.remove(filePath)
                FileHelper.waitForFileToBeRemoved(filePath)
            except OSError as e:
                PrintMessage(f"Failed with: {e.strerror}")
                PrintMessage(f"Error code: {e.code}")

    def _saveScreenshot(self, filePath):
        PrintMessage(f"SYSTEM: Saving screenshot {filePath}")
        self._removeExistingScreenshot(filePath)

        tryExecute(Screenshot(self.webdriver).fullScreenshot, imagePath=filePath)

        PrintMessage("SYSTEM: Saving screenshot complete.")

    def makeScreenshot(self, testName, folderName=None):
        """
        Screenshot lands in screenshot folder
        Screenshot file name is composed of test name & random string
        On re-run new screenshots will be saved with unique random string
        """
        if folderName is None:
            folderName = self.testContext.getRequiredFolders(self.screenshotFolderName)

        screenshotName = f"{testName}_{getUniqueAlphaNumericString('')}.png"
        filePath = os.path.join(folderName, screenshotName)

        self._saveScreenshot(filePath)
        return filePath

    def saveNetworkLogs(self):
        folderName = self.testContext.getRequiredFolders("logging")
        logName = f"perf_log_C{self.testContext.currentTestId}_{getUniqueAlphaNumericString('')}.json"
        filePath = os.path.join(folderName, logName)

        # Extract network logs
        logs = self.webdriver.get_log('performance')
        results = []
        for entry in logs:
            log = json.loads(entry['message'])  # Parse the JSON message
            message = log['message']

            if message['method'] == 'Network.responseReceived':
                response = message['params']['response']

                # below, capture logs with the response body

                # requestId = message['params']['requestId']
                # try:
                #     responseBody = webdriver.execute_cdp_cmd(
                #         'Network.getResponseBody', {'requestId': requestId}
                #     )
                #     response["response_body"] = responseBody['body']
                # except Exception as e:
                #     print(f"Could not fetch response body for requestId: {requestId}")

                results.append(response)

            elif message['method'] == 'Network.requestWillBeSent':
                request = message['params']['request']
                results.append(request)

        with open(filePath, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(results))

    def makeTestEvidenceScreenshot(self, stageName):
        """
        Screenshot lands in testEvidence folder
        Screenshot file name is composed of test name & stage/phase name
        """
        if not self.testContext.getSetting(ConfigOptions.GATHER_SCREENSHOT_EVIDENCE):
            return None

        if self.testContext.currentTestId:
            testEvidenceFolder = os.path.join(self.testContext.getRequiredFolders(self.evidenceFolderName), str(self.testContext.currentTestId))
        elif self.testContext.clientOnboardingEvidenceFolderName:
            testEvidenceFolder = os.path.join(self.testContext.getRequiredFolders(self.evidenceFolderName), str(self.testContext.clientOnboardingEvidenceFolderName))
        else:
            testEvidenceFolder = self.testContext.getRequiredFolders(self.evidenceFolderName)

        tryExecute(os.makedirs, testEvidenceFolder, exist_ok=True)

        screenshotPath = os.path.join(testEvidenceFolder, f"{stageName}-{getTimeStamp()}.png")
        self._saveScreenshot(screenshotPath)
        return screenshotPath
