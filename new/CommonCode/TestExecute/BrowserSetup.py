import platform
from selenium.webdriver import ChromeOptions, EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.remote.webdriver import WebDriver
from CommonCode.CustomExceptions import UIException
from CommonCode.Driver.PyStormDriver import PyStormDriver
from CommonCode.Driver.PyStormElement import PyStormElement
from CommonCode.TestExecute.ExecuteEnums import BrowserEnum, ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import TestContext


class BrowserSetup:
    """
    Chrome versions: https://chromedriver.storage.googleapis.com/
    Edge versions: https://msedgedriver.azureedge.net/
    """

    def __init__(self, testContext: TestContext):
        self.testContext = testContext
        self.browserConfig = self.testContext.browserConfig

    def _disableDownloadPrompt(self, webdriver: WebDriver):
        webdriver.command_executor._commands["send_command"] = (
            "POST", "/session/$sessionId/chromium/send_command")

        params = {
            "cmd": "Page.setDownloadBehavior",
            "params": {
                "behavior": "allow",
                "downloadPath": self.testContext.testDownloadFolder
            }
        }
        webdriver.execute("send_command", params)

    def _logToConsole(self, webdriver: WebDriver):
        if "version" in webdriver.capabilities:
            PrintMessage(f"Browser version: {webdriver.capabilities['version']}")
        elif "driverVersion" in webdriver.capabilities:
            PrintMessage(f"Browser version: {webdriver.capabilities['driverVersion']}")

    def _getChromeOptions(self):
        chromeOptions = ChromeOptions()

        chromeOptions.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        if self.testContext.getSetting(ConfigOptions.RUN_HEADLESS):
            if self.testContext.getSetting(ConfigOptions.RUN_SHELL_BINARY):
                PrintMessage(
                    f"Browser Setup > HEADLESS > Using chrome-shell binary: '{self.browserConfig.getSetting(ConfigOptions.CHROME_SHELL_PATH)}'",
                    inStepMessage=True)
                chromeOptions.binary_location = self.browserConfig.getSetting(ConfigOptions.CHROME_SHELL_PATH)
            else:
                PrintMessage("Browser Setup > HEADLESS > Using chrome", inStepMessage=True)
            chromeOptions.add_argument("--headless")

        if platform.system() == "Linux":
            chromeOptions.add_argument("--no-sandbox")
            chromeOptions.add_argument("--disable-dev-shm-usage")
            chromeOptions.add_argument("--ignore-gpu-blacklist")
            chromeOptions.add_argument("--use-gl")

        # decreases number of non PyStorm related output
        chromeOptions.add_argument('--log-level=3')
        chromeOptions.add_argument("start-maximized")
        chromeOptions.add_experimental_option("excludeSwitches", ["enable-logging"])
        return chromeOptions

    def _getEdgeOptions(self):
        edgeOptions = EdgeOptions()
        if self.testContext.getSetting(ConfigOptions.RUN_HEADLESS):
            edgeOptions.add_argument("--headless")

        if platform.system().lower() == "linux":
            edgeOptions.add_argument("--no-sandbox")
            edgeOptions.add_argument("--disable-dev-shm-usage")
            edgeOptions.add_argument("--ignore-gpu-blacklist")
            edgeOptions.add_argument("--use-gl")

        edgeOptions.add_experimental_option("prefs", {"download.default_directory": self.testContext.testDownloadFolder})
        edgeOptions.add_experimental_option("excludeSwitches", ["enable-logging"])

        return edgeOptions

    def setup(self) -> PyStormDriver:
        """
        Browser can be selected either via configuration file or via command line
        Command line has precedence over configuration file
        """
        webdriverPath = self.browserConfig.getSetting(ConfigOptions.DRIVER_PATH)

        match self.browserConfig.getSetting(ConfigOptions.BROWSER):
            case BrowserEnum.CHROME_DOCKER:
                browserOptions = self._getChromeOptions()
                webdriver = PyStormDriver(options=browserOptions)

            case BrowserEnum.CHROME:
                browserOptions = self._getChromeOptions()
                webdriver = PyStormDriver(service=ChromeService(webdriverPath), options=browserOptions)

            case BrowserEnum.EDGE:
                browserOptions = self._getEdgeOptions()
                webdriver = EdgeDriver(service=EdgeService(webdriverPath), options=browserOptions)

            case _:
                raise UIException("Unknown browser/ browser version")

        webdriver.set_window_size(width=1920, height=1080)
        webdriver._web_element_cls = PyStormElement
        self._logToConsole(webdriver)
        self._disableDownloadPrompt(webdriver)

        return webdriver
