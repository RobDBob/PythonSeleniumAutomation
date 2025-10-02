import copy
import requests
from bs4 import BeautifulSoup
from CommonCode.TestExecute.Logging import PrintMessage


class RaptorRequests:
    FNZ_COOKIE_NAME = 'FNZ'
    TS_COOKIE_NAME_1 = 'TS01eb8bed'
    TS_COOKIE_NAME_2 = 'TS581beb71027'

    def __init__(self, webdriver):
        self.webdriver = webdriver

        self.baseUrl = "https://adminae42.fnzc.co.uk/admin/soap/"
        self.session = self.configureSession()

    def addCookieFromCookie(self, session: requests.Session, cookieName: str):
        webdriverCookie = self.webdriver.get_cookie(cookieName)

        # ignoring unwanted cookies
        if "sameSite" in webdriverCookie:
            webdriverCookie.pop("sameSite")
        if "httpOnly" in webdriverCookie:
            value = webdriverCookie.pop("httpOnly")
            webdriverCookie["rest"] = {"HttpOnly": value}

        PrintMessage(f"Added cookie: {webdriverCookie.get('name', '')}")
        session.cookies.setSetting(**webdriverCookie)

    def configureSession(self):
        session = requests.Session()

        self.addCookieFromCookie(session, RaptorRequests.FNZ_COOKIE_NAME)
        self.addCookieFromCookie(session, RaptorRequests.TS_COOKIE_NAME_1)
        self.addCookieFromCookie(session, RaptorRequests.TS_COOKIE_NAME_2)

        return session

    def executeRequest(self, method, url, **kwargs):
        """
        Generic method for request execution
        method: GET/PUT etc
        """
        session: requests.Session = copy.deepcopy(self.session)
        response = session.request(method, url, **kwargs)
        return response

    def getLogResponseXML(self, soapUrl):
        xmlResponseIndex = 1
        url = f"{self.baseUrl}{soapUrl}"

        response = self.executeRequest("GET", url)
        soup = BeautifulSoup(response.content, "html.parser")
        found = soup.body.find_all("textarea")
        if found:
            return found[xmlResponseIndex]
        PrintMessage("API: getLogResponseXML request failed")
        PrintMessage(response)
        return None
