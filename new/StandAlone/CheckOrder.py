import sys
from CommonCode.API.Wrap.PlatformRequestsHelper import PlatformRequestsHelper
from CommonCode.TestExecute.BrowserSetup import BrowserSetup
from CommonCode.TestExecute.TestContext import ConfigOptions, Test_Context
from TestPages.PlatformLoginPage import PlatformLoginPage


def checkOrder(accountNumber, apiSessionHeaders):
    platformAPIRequestsHelper = PlatformRequestsHelper(apiSessionHeaders, Test_Context)
    openOrders = platformAPIRequestsHelper.getOpenOrdersBathesForAccount(accountNumber)
    print(f"Open orders are: {openOrders}")


def closeOrder(accountNumber, apiSessionHeaders):
    platformAPIRequestsHelper = PlatformRequestsHelper(apiSessionHeaders, Test_Context)
    platformAPIRequestsHelper.closeAnyOpenOrdersForAccount(accountNumber, 147)


if __name__ == "__main__":
    # execute code: python -m StandAlone.CheckOrder check te5chromeTestServer WP1547432
    # code requires webdriver & chrome to run

    assert len(sys.argv) > 3, "Expected 3 parameters: close/check, configName, accountNumber"

    Test_Context.setSetting(ConfigOptions.CURRENT_CONFIG_NAME, sys.argv[2])
    Test_Context.setSetting(ConfigOptions.RUN_HEADLESS, True)
    Test_Context.updateFromConfigFile()
    driver = BrowserSetup(Test_Context).setup()
    PlatformLoginPage(driver).logAsUser(userNumber=55)

    if sys.argv[1] == "close":
        closeOrder(sys.argv[3], driver.apiSessionHeaders)
    else:
        checkOrder(sys.argv[3], driver.apiSessionHeaders)
