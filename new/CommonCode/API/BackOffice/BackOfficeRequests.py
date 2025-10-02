import logging
import re
import requests
from retry import retry
from CommonCode.API.APIHelper import cleanUpRawResponseText
from CommonCode.API.BackOffice.Data.PooledCompletionDetails import PooledCompletionDetails
from CommonCode.API.BackOffice.Data.WrapOrdersData import WrapOrdersData
from CommonCode.CustomExceptions import AccessDeniedException, APIException
from CommonCode.TestExecute.Logging import PrintMessage


class BackOfficeRequests:
    """
    <input type="hidden" name="webauditlogid" id="webauditlogid" value="2148927578" />
    use regex to get audit log out from getPooledDeals() "webauditlogid" value="(\\d*)"

    Since its all comms with ASPX pages, there is a lot of text reponse being passed around
    """
    HEADERS = {"Accept": "*",
               "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
               'Accept-Encoding': "gzip, deflate, br",
               "Content-Type": "application/x-www-form-urlencoded"}

    def __init__(self, baseUrl, userName, userPassword):
        self.authCookies = {}
        self.webAuditLogId = None
        self.baseUrl = baseUrl

        self._logIn(userName, userPassword)

    def _setCookies(self, cookies):
        for cookie in cookies:
            self.authCookies[cookie[0]] = cookie[1]

    def _setWebAuditLogId(self, bodyText):
        reSearchResult = re.search(r'webauditlogid" value="(\d*)', bodyText)
        if reSearchResult:
            self.webAuditLogId = int(reSearchResult.group(1))

    def _getSuccessConfirmation(self, bodyText):
        reSearchResult = re.search(r'<h4>SUMMARY: (.*)<\/h4>', bodyText)
        if reSearchResult:
            return reSearchResult.group(1)
        return ""

    def executeRequest(self, method, url, **kwargs):
        session: requests.Session = requests.Session()
        if method == 'POST' and "data" in kwargs and kwargs["data"].get("webauditlogid", None):
            kwargs["data"]["webauditlogid"] = self.webAuditLogId
        response = session.request(method, url, headers=self.HEADERS, cookies=self.authCookies, **kwargs)
        self._setWebAuditLogId(response.text)
        if not response.ok:
            PrintMessage(f"BackOffice request failed to {method}:{url}", level=logging.error)
            PrintMessage(f"Request headers {session.headers.items()}", level=logging.error)
            PrintMessage(f"Request cookies {session.cookies.items()}", level=logging.error)

        if "Access Denied" in response.text:
            raise AccessDeniedException()
        return response

    def _logIn(self, userName, userPassword):
        url = f"{self.baseUrl}/home.aspx"
        data = {'txtusername': userName, 'txtpassword': userPassword}
        response = self.executeRequest("POST", url, data=data)
        self._setCookies(response.cookies.iteritems())

    @retry(exceptions=APIException, delay=2, tries=5)
    def postPrePooledDeals(self, expectedSuccess=True, **kwargs):
        requestData = {"actiontype": "AutoPlaceBatches",
                       "webauditlogid": self.webAuditLogId,
                       "managerid": None,
                       "instrumentcode": None,
                       "orderbuysell": None,
                       "autoplacebatchids": None}
        requestData.update(kwargs)
        url = f"{self.baseUrl}/deals/managedfunds/prepooleddeals.aspx"

        response = self.executeRequest("POST", url, data=requestData)
        if expectedSuccess:
            confirmation = self._getSuccessConfirmation(response.text)
            if "successfully" not in confirmation:
                raise APIException("postDealsAutoPlaceOrderBatch> Unsuccesfull placement")
        return cleanUpRawResponseText(response.text)

    def getPooledDeals(self):
        url = f"{self.baseUrl}/deals/managedfunds/pooledapplications.aspx"
        return self.executeRequest("GET", url)

    def postPooledCompletion(self, data):
        """
        Deals > Managed Funds > Pooled Completions > Fill Price / value/ Quantity - GO Button
        """
        url = f"{self.baseUrl}/deals/managedfunds/pooledcompletions.aspx"
        return self.executeRequest("POST", url, data=data)

    def getPooledCompletion(self, batchId):
        url = f"{self.baseUrl}/deals/managedfunds/pooledcompletions.aspx?batchid={batchId}"
        return self.executeRequest("GET", url)

    def authorisePooledCompletions(self, method, data=None):
        url = f"{self.baseUrl}/deals/managedfunds/authorisepooledcompletions.aspx"
        response = self.executeRequest(method, url, data=data)
        return cleanUpRawResponseText(response.text)

    def getWrapOrders(self, **kwargs):
        """
        Returns list of dictionaries
        Represents table from Deals > Wrap Orders
        """
        requestData = {"actiontype": "search",
                       "orderid": None,
                       "batchid": None,
                       "SearchStandingBatchID": None,
                       "SearchStatus": "ALL",
                       "SearchBatchID": None,
                       "SearchSecurityType": None,
                       "SearchOrderID": None,
                       "SearchBatchType": "Auto or One-Off",
                       "SearchClAccountID": None,
                       "SearchCompany": "ALL ex DEMO",
                       "SearchEFMDealReference": None}
        requestData.update(kwargs)
        url = f"{self.baseUrl}/deals/orders/WrapOrders.aspx"
        response = self.executeRequest("POST", url, data=requestData)
        return WrapOrdersData(cleanUpRawResponseText(response.text))

    def getPooledOrderDetails(self, searchPoolOrderID):
        url = f"{self.baseUrl}/popups/PooledOrderDetail.aspx"
        params = {"SearchPoolOrderID": searchPoolOrderID}
        response = self.executeRequest("POST", url, params=params)
        return PooledCompletionDetails(cleanUpRawResponseText(response.text))

    def maintenanceTabFindUsersRequest(self, data):
        """
        Maintenance tab > Find User > Fill UserLogon / status/ Staff user - Search Button
        """
        url = f"{self.baseUrl}/Maintenance/website/FindUsers.aspx"
        response = self.executeRequest("POST", url, data=data)
        return cleanUpRawResponseText(response.text)

    def maintenanceTabMaintainUserRequest(self, **kwargs):
        """
        Navigate to Maintenance tab > User Site Access
        """
        url = f"{self.baseUrl}/Maintenance/website/MaintainUser.aspx"
        response = self.executeRequest(kwargs.get("method"), url, data=kwargs.get("data"), params=kwargs.get("params"))

        if kwargs.get("responseObject"):
            return response
        return cleanUpRawResponseText(response.text)

    def uploadChequeCash(self, data):
        """
        Maintenance tab > It Tool > Upload payments
        """
        url = f"{self.baseUrl}/Maintenance/Testing/UploadPayments.aspx"
        response = self.executeRequest("POST", url, data=data)
        return cleanUpRawResponseText(response.text)

    def maintenanceTabUserSiteAccessRequest(self, **kwargs):
        """
        Navigate to Maintenance tab > User Site Access
        """
        url = f"{self.baseUrl}/Maintenance/website/UserSiteAccess.aspx"
        response = self.executeRequest(kwargs.get("method"), url, data=kwargs.get("data"), params=kwargs.get("params"))
        return cleanUpRawResponseText(response.text)
