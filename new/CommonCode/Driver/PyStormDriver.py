import json
import logging
from time import sleep
from retry import retry
from selenium.webdriver.chrome.webdriver import WebDriver
from CommonCode.API import APIConstants
from CommonCode.API.Wrap.Requests.WrapDriverSessionToAPI import WrapDriverSessionToAPI
from CommonCode.CustomExceptions import APIException
from CommonCode.Driver.PyStormSwitchTo import PyStormSwitchTo
from CommonCode.TestExecute.Logging import PrintMessage

# pylint: disable=invalid-name


class PyStormDriver(WebDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._switch_to = PyStormSwitchTo(self)

    def _cookiesAreAvailable(self):
        return self.get_cookie(APIConstants.ANTIFORGERY_COOKIE_NAME)

    @retry(exceptions=APIException, delay=5, tries=3)
    def _forceNavigationAndWaitForCookies(self, currentUrl):
        from urllib.parse import urljoin
        hostUrl = urljoin(currentUrl, '/')
        if self._cookiesAreAvailable():
            return

        self.get(f"{hostUrl}/wpadviser/en-gb/dashboard/home/main/customer")
        sleep(2)
        self.get(currentUrl)

        if not self._cookiesAreAvailable():
            raise APIException("No cookies found.")

    @retry(exceptions=APIException, tries=10, delay=2)
    def waitForAPIRequestToFinish(self, partialURL):
        """
        Method to slow down test execution
        It checks for performance logs containing unfinished requests for given URL

        URL: partial URL of an request that executes last on navigating to a webpage
        """
        if self.getNetworkResponseReceived(partialURL):
            PrintMessage("Request logs exists - retrying", inStepMessage=True)
            raise APIException("perf logs there, retry")

    def getNetworkResponseReceived(self, partialURL):
        perfLogs = [json.loads(k["message"]) for k in self.get_log("performance")]
        method = "Network.responseReceived"

        matchingLogs = [k for k in perfLogs if method in k.get("message", {}).get("method", "")]

        if matchingLogs:
            return [k for k in matchingLogs if partialURL in k.get("message", {}).get("params", {}).get("response", {}).get("url", "")]

        return None

    def download_file(self, *args, **kwargs):
        raise NotImplementedError

    def get_downloadable_files(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def apiSessionHeaders(self) -> dict:
        self._forceNavigationAndWaitForCookies(self.current_url)

        PrintMessage("Platform requests session configured.", logging.DEBUG, inStepMessage=True)
        return WrapDriverSessionToAPI(self.get_cookies()).headers
