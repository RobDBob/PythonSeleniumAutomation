import unittest
from CommonCode.API.BackOffice.BackOfficeHelper import BackOfficeHelper
from CommonCode.API.BackOffice.BackOfficeUserHelper import BackOfficeUserHelper
from CommonCode.API.Wrap.PlatformRequestsHelper import PlatformRequestsHelper
from CommonCode.CustomExceptions import APIException
from CommonCode.HelperFunctions import getTestIdFromTestName
from CommonCode.Models.AccountDataObj import AccountDataObj
from CommonCode.TestExecute import Constants as Const
from CommonCode.TestExecute.BrowserSetup import BrowserSetup
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context, TestContext
from CommonCode.TestHelpers.BrowserHelper import BrowserHelper
from CommonCode.TestHelpers.DocumentDownloader import DocumentDownloader
from TestData.TestDataLoader import TestDataLoader
from TestData.TestUsers.TestUsersEnum import UserType
from TestPages import DataEnums
from TestPages.BatemanLoginPage import BatemanLoginPage
from TestPages.PlatformGenericLoginPage import PlatformGenericLoginPage
from TestPages.PlatformLoginPage import PlatformLoginPage
from TestPages.PlatformPage import PlatformPage
from TestPages.SLADMIN.SLAdminLoginPage import SLAdminLoginPage


class BaseTestClass(unittest.TestCase):
    ADO_TEST_SUITE = None
    TEST_USER_NUMBER = None
    webdriver = None
    testContext: TestContext = None
    platformAPIRequestsHelper: PlatformRequestsHelper = None

    _documentDownloader = None

    @classmethod
    def setUpClass(cls):
        cls.testContext = Test_Context
        cls.testContext.currentTestClassName = cls.__name__
        cls.longMessage = True

    @classmethod
    def tearDownClass(cls):
        if cls.webdriver:
            cls.webdriver.quit()

    def setUp(self):
        PrintMessage(Const.TEST_HEAD.format(self._testMethodName))

        self.addCleanup(self.closeBrowser)
        self.testContext.currentTestId = getTestIdFromTestName(self._testMethodName)
        self.startBrowser()
        self.platformAPIRequestsHelper = None

    def tearDown(self):
        PrintMessage(f"{Const.TEST_TAIL} - test result: {self._outcome.result}")

        result = self._outcome.result
        ok = all(test != self for test, text in result.errors + result.failures)
        if not ok:
            BrowserHelper(self.webdriver, self.testContext).makeScreenshot(self._testMethodName)

        if self.testContext.getSetting(ConfigOptions.CAPTURE_NETWORK_LOGS):
            BrowserHelper(self.webdriver, self.testContext).saveNetworkLogs()

    def startBrowser(self):
        self.webdriver = BrowserSetup(self.testContext).setup()

    def closeBrowser(self):
        if self.webdriver:
            self.webdriver.quit()
            self.webdriver = None

    def restartBrowser(self):
        self.closeBrowser()
        self.startBrowser()
        self.platformAPIRequestsHelper = None

    def setPlatformRequestHelper(self, reset=False):
        try:
            if self.platformAPIRequestsHelper is None or reset:
                self.platformAPIRequestsHelper = PlatformRequestsHelper(self.webdriver.apiSessionHeaders, self.testContext)

        except APIException:
            PrintMessage("Failed to set platformAPIRequestsHelper, cookies were not available.")

    def logAsUser(self, userNumber, reLog=False) -> PlatformPage:
        if reLog:
            self.restartBrowser()

        platformPage = PlatformLoginPage(self.webdriver).logAsUser(userNumber)
        self.setPlatformRequestHelper()
        return platformPage

    def logAsUserToDisplayDashboardPage(self, userNumber, reLog=False):
        """
        Login function where the user redirects to Dashboard page as Platform page after successful Login
        """
        if reLog:
            self.restartBrowser()

        platformPage = PlatformLoginPage(self.webdriver).logAsUserToDisplayDashboardPage(userNumber)
        self.setPlatformRequestHelper()
        return platformPage

    def logAsUserAsAdviserInternalManagement(self, userNumber, reLog=False):
        """
        Login function where the user redirects to Landing page as Platform page after successful Login for L2_Adviser_Management
        """
        if reLog:
            self.restartBrowser()

        return PlatformLoginPage(self.webdriver).logAsUserAsAdviserInternalManagement(userNumber)

    def logOntoPlatformWithUserType(self, userType: UserType, reLog=False):
        if reLog:
            self.restartBrowser()

        platformPage = PlatformLoginPage(self.webdriver).performLoginWithUserType(userType)
        self.setPlatformRequestHelper()
        return platformPage

    def getTestData(self, fileName, sectionName=None):
        dataLoader = TestDataLoader(self.environmentName)

        if "yaml" in fileName or "yml" in fileName:
            return dataLoader.getTestDataFromYmlFile(fileName, sectionName)
        return dataLoader.getTestDataFromYmlFile(fileName, sectionName)

    def getTestDataObject(self, fileName, sectionName=None):
        return AccountDataObj(self.getTestData(fileName, sectionName))

    def getExpectedLoginPage(self, expectedPageToOpen=None, reLog=False):
        if reLog:
            self.restartBrowser()
        if expectedPageToOpen == DataEnums.SL_ADMIN_PAGE:
            return SLAdminLoginPage(self.webdriver)
        if expectedPageToOpen == DataEnums.BATEMAN_PAGE:
            return BatemanLoginPage(self.webdriver)
        return None

    def loginAsUniPass(self, userKey, expectedPageToOpen, relog=False) -> PlatformPage:
        genericLogInPage = self.getExpectedLoginPage(expectedPageToOpen, reLog=relog)
        unipassLoginPage = genericLogInPage.navigateToUnipassLogin()
        platformPage: PlatformPage = unipassLoginPage.performLogin(*self.testContext.testUsers.getUserByKey(userKey))
        self.setPlatformRequestHelper()
        return platformPage

    def getPlatformAdviserLoginPage(self, reLog=False):
        if reLog:
            self.restartBrowser()
        platformPage = PlatformGenericLoginPage(self.webdriver)
        self.setPlatformRequestHelper()
        return platformPage

    def closeAnyOpenOrdersForAccount(self, accountNumber):
        PrintMessage(f">>> closeAnyOpenOrdersForAccount - closing any open deals for account: '{accountNumber}'")
        self.setPlatformRequestHelper()
        self.platformAPIRequestsHelper.closeAnyOpenOrdersForAccount(accountNumber, self.TEST_USER_NUMBER)
        PrintMessage(f">>> closeAnyOpenOrdersForAccount - closing any open deals for account: '{accountNumber}' - DONE")

    def uploadCashForCheques(self, accountNumber, amount):
        """
        Function : Login to BackOffice and Upload cash for cheque payment method for a particular WP
        """
        boUserName, boUserPassword = self.testContext.testUsers.getBOUserByNumber(self.TEST_USER_NUMBER)
        backOffice = BackOfficeHelper(self.testContext.getSetting(ConfigOptions.BACK_OFFICE_URL), boUserName, boUserPassword)
        backOffice.uploadCash(accountNumber, amount)

    def setDealToComplete(self, batchNumber, orderNumber):
        boUserName, boUserPassword = self.testContext.testUsers.getBOUserByNumber(self.TEST_USER_NUMBER)
        backOffice = BackOfficeHelper(self.testContext.getSetting(ConfigOptions.BACK_OFFICE_URL), boUserName, boUserPassword)
        backOffice.setDealToComplete(batchNumber, orderNumber)

    def getBOUser(self, userNumber):
        """
        Function : Login to BackOffice and get the UserType and User Site access Status
        """
        PrintMessage("BaseTestClass > Get the Back office Credentials, UserLogon details from the UserNumber and Login to BackOffice")
        boUserName, boUserPassword = self.testContext.testUsers.getBOUserByNumber(userNumber)
        userName, _ = self.testContext.testUsers.getUserByNumber(userNumber)
        backOfficeUsers = BackOfficeUserHelper(self.testContext.getSetting(ConfigOptions.BACK_OFFICE_URL), boUserName, boUserPassword)
        PrintMessage("BaseTestClass > Get the Back office User type and User Site access Status")
        return backOfficeUsers.getBOUserByUserLogon(userName)

    @property
    def documentDownloader(self):
        # Using downloader will change webdriver state
        if not self._documentDownloader:
            self._documentDownloader: DocumentDownloader = DocumentDownloader(self.webdriver, self.testContext)
        return self._documentDownloader

    @property
    def environmentName(self):
        return self.testContext.getSetting(ConfigOptions.ENVIRONMENT)
