import logging
from datetime import datetime
import requests
from CommonCode.API.APIHelper import cleanUpRawResponseText, isResponseJSON, paramsToURL
from CommonCode.CustomExceptions import APIException
from CommonCode.TestExecute.Logging import PrintMessage


class PlatformRequests:
    """
    Functionality implemented in this class will only work after webdriver established session with platform i.e. user is logged in
    """

    def __init__(self, wrapAPISessionHeaders: dict, slWrapUrl: str):
        self.requestHeaders = wrapAPISessionHeaders
        self.slWrapUrl = slWrapUrl

    def executeRequest(self, method, url, **kwargs):
        """
        Generic method for request execution
        method: GET/PUT etc
        """
        session: requests.Session = requests.Session()
        session.headers = kwargs.get("headers") if kwargs.get("headers") else self.requestHeaders
        response = session.request(method, url, **kwargs)

        if "AccessDenied" in response.url:
            PrintMessage(response.history, level=logging.DEBUG)
            raise APIException("Access denied - request failed")
        PrintMessage(f"Platform Requests > '{method}:{response.url}'", level=logging.DEBUG)
        return response

    def customerSearch(self, params):
        """
        Returns customer list
        """
        PrintMessage(f"Platform Requests > customerSearch with  params: '{params}'", level=logging.DEBUG)
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/customersearch/get"
        response = self.executeRequest("GET", url, params=params)

        if isResponseJSON(response):
            return response.json().get("Result", {}).get("CustomerList", [])
        PrintMessage("Platform Requests > customerSearch request failed.", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return {}

    def getCustomerAccount(self, customerId) -> list:
        PrintMessage(f"Platform Requests > getCustomerAccount with customerId: '{customerId}'", level=logging.DEBUG)
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/customerunderlyingaccountdetails/get?customerId={customerId}"
        response = self.executeRequest("GET", url)
        if isResponseJSON(response):
            return response.json().get("Result", [])

        PrintMessage("Platform Requests > getCustomerAccount request failed", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return []

    def getProductValuationSummaryDetails(self, urlParams):
        """
        Using urlParams as there might be duplicated keys for subaccount hierarchy ids
        """
        PrintMessage(f"Platform Requests > getSummaryDetails with params: '{urlParams}'", level=logging.DEBUG)
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/transformation/newproductsvaluationdetailsummary/get{urlParams}"
        response = self.executeRequest("GET", url)

        if isResponseJSON(response):
            return response.json().get("Result", [])

        PrintMessage("Platform Requests > getSummaryDetails request failed", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return []

    def getPortFolioInvestment(self, params):
        PrintMessage(f"Platform Requests > getPortFolioInvestment with params: '{params}'", level=logging.DEBUG)
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/portfolioanalysis/investment/portfolioinvestment/get?{paramsToURL(params)}"

        response = self.executeRequest("GET", url)
        if isResponseJSON(response):
            return response.json().get("Result", {})

        PrintMessage("Platform Requests > getPortFolioInvestment request failed", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return {}

    def organizationSearch(self, accountNumber, orgName):
        params = {"organisationId": "",
                  "organisationStatus": 2,
                  "customerType": 0,
                  "businessType": "",
                  "companyType": "",
                  "organisationName": orgName,
                  "clAccountId": accountNumber,
                  "isPartialOrganisationName": True,
                  "organisationRole": "",
                  "entityType": "",
                  "entityId": "",
                  "visibleToAdviserId": "",
                  "currentPage": 1,
                  "pageSize": 20}
        PrintMessage(f"Platform Requests > organizationSearch with params: '{params}'", level=logging.DEBUG)
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/organisationsearch/get"
        response = self.executeRequest("GET", url, params=params)
        if isResponseJSON(response):
            return response.json().get("Result", [])

        PrintMessage("Platform Requests > organizationSearch request failed", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return []

    def customerSearchActorName(self, accountNumber):
        """
        Params:
        accountNumber: WPxxxxxx
        """
        params = {"inputString": accountNumber}
        PrintMessage(f"Platform Requests > customerSearchActorName with params: '{params}'", level=logging.DEBUG)
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/searchactorname/get"
        response = self.executeRequest("GET", url, params=params)
        if isResponseJSON(response):
            return response.json().get("Result", [])

        PrintMessage("Platform Requests > customerSearchActorName request failed", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return []

    def getClientOrders(self, accountNumber):
        PrintMessage(f"Platform Requests > getClientOrders with accountNumber: '{accountNumber}'", level=logging.DEBUG)
        params = {"claccountid": accountNumber, "todate": datetime.now().strftime("%Y-%m-%d")}
        url = f"{self.slWrapUrl}/clients/orders/orders.aspx"
        response = self.executeRequest("GET", url, params=params)
        return cleanUpRawResponseText(response.text)

    def regularWithdrawal(self, method, data, params=None):
        url = f"{self.slWrapUrl}/clients/cash/RegularWithdrawals.aspx"
        response = self.executeRequest(method, url, params=params, data=data)
        return cleanUpRawResponseText(response.text)

    def getCashEntries(self, accountNumber):
        url = f"{self.slWrapUrl}/clients/cash/Cash-Entries.aspx"
        params = {"claccountid": accountNumber}
        response = self.executeRequest("GET", url, params=params)
        return cleanUpRawResponseText(response.text)

    def executeAuthoriseProcessesRequest(self, method, data=None):
        url = f"{self.slWrapUrl}/Admin/Authorisations/AuthoriseProcess.aspx"
        headers = self.requestHeaders
        headers["content-type"] = "application/x-www-form-urlencoded"
        response = self.executeRequest(method, url, data=data, headers=headers)
        return cleanUpRawResponseText(response.text)
