import os
from CommonCode.JsonReader import JsonReader
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Objects.ConfigClass import ConfigClass
from TestData.TestUsers.TestUsers import TestUsers


class TestContext(ConfigClass):
    """
    Bridge class between test runner and unittest
    It contains test environment information
    """
    testData = {}
    settings = {}
    _testUsers = None

    # holds data for current execution
    currentTestClassName = None
    currentTestId = None
    failedWindowHandle = None
    initialWindowHandle = None

    # folder for evidence screenshots
    clientOnboardingEvidenceFolderName = None

    def __init__(self):
        super().__init__()

        configFileName = "BrowserConfig.yaml" if not self.getSetting(ConfigOptions.DOCKER_RUN) else "BrowserDockerConfig.yaml"
        self.setSettingFromYml(configFileName, ConfigOptions.BROWSER_CONFIG)

        self.setSettingFromYml("SetupConfig.yaml", ConfigOptions.SETUP_CONFIG)

    def updateFromConfigFile(self):
        """
        Updates test context from configuration file
        Current values in Test Context have higher priorty than configuration file
        """
        currentConfigName = self.getSetting(ConfigOptions.CURRENT_CONFIG_NAME)
        configPath = f"./ConfigFiles/TestRunConfig_{currentConfigName}.json"
        if not currentConfigName or not os.path.exists(configPath):
            print(f"Encountered problem, configuration file at '{configPath}' not found.")

        automationData = JsonReader(configPath).load("TestAutomation")
        self.update(automationData)

    def getRequiredFolders(self, folderName):
        try:
            return self.setupConfig.getSetting(ConfigOptions.REQUIRED_FOLDERS)[folderName]
        except KeyError:
            return None

    def setSessionTestData(self, testId, testData):
        """sets semi-peristent test data to be used during test

        Args:
            testId (int): indicates numeric value for testId
            settingValue (any/str): testData structure, can be of any type as long other end is aware
        """
        self.testData[testId] = testData

    def getSessionTestData(self, testId):
        """gets semi-peristent test data to be used during test

        Args:
            testId (int): indicates numeric value for testId
        """
        return self.testData.get(testId)

    @property
    def testUsers(self):
        if not self._testUsers:
            self._testUsers = TestUsers()
        return self._testUsers

    @property
    def browserConfig(self) -> ConfigClass:
        return self.getSetting(ConfigOptions.BROWSER_CONFIG)

    @property
    def setupConfig(self) -> ConfigClass:
        return self.getSetting(ConfigOptions.SETUP_CONFIG)

    @property
    def testDownloadFolder(self):
        return os.path.join(os.getcwd(), self.getRequiredFolders('downloads'), str(self.currentTestId))


# global Test_Context
Test_Context = TestContext()
