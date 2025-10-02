from retry import retry
from selenium.common.exceptions import TimeoutException
from CommonCode.API.Wrap.PlatformRequestsHelper import PlatformRequestsHelper
from CommonCode.TestExecute.BrowserSetup import BrowserSetup
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context
from TestPages.PlatformLoginPage import PlatformLoginPage


@retry(exceptions=TimeoutException, delay=30, tries=5)
def logAsUser(userNumber):
    Test_Context.setSetting(ConfigOptions.RUN_HEADLESS, True)
    webdriver = BrowserSetup(Test_Context).setup()
    return PlatformLoginPage(webdriver).logAsUser(userNumber)


def rejectAllTrustRequestsAPI():
    """
    Method will reject all existing requests
    """
    PrintMessage("rejectAllTrustRequestsAPI > logging in to retrieve API headers")
    firstTestUserNumber = 157
    platformPage = logAsUser(userNumber=firstTestUserNumber)
    platformAPIRequestsHelper = PlatformRequestsHelper(platformPage.webdriver.apiSessionHeaders, Test_Context)
    PrintMessage("rejectAllTrustRequestsAPI > rejecting all trust requests - START")
    platformAPIRequestsHelper.rejectAllAuthoriseProcesses()
    PrintMessage("rejectAllTrustRequestsAPI > rejecting all trust requests - STOP")


if __name__ == '__main__':
    CommandLineArgumentsParser.processArgumentsEnvironmentSelection(Test_Context)
    rejectAllTrustRequestsAPI()
