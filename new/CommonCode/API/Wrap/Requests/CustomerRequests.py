import copy
import json
import requests
from CommonCode.CustomExceptions import APIExceptionSessionExpired
from CommonCode.TestExecute.Logging import PrintMessage


class CustomerRequests:
    def __init__(self, apiSessionHeaders: dict, slWrapUrl):
        self.session = self._createSession(apiSessionHeaders)
        self.slWrapUrl = slWrapUrl

    def _createSession(self, apiSessionHeaders: dict):
        session = requests.Session()

        session.headers.update(apiSessionHeaders)
        return session

    def executeRequest(self, method, url, **kwargs):
        """
        Generic method for request execution
        method: GET/PUT etc
        """
        defaultReferer = "https://slwrapte5.fnz.co.uk/clients/cash/regularwithdrawals.aspx?claccountid=WP1801619-003"
        session: requests.Session = copy.deepcopy(self.session)

        session.headers["Referer"] = kwargs.pop("referer") if "referer" in kwargs else defaultReferer

        response = session.request(method, url, **kwargs)

        if "AccessDenied" in response.url:
            PrintMessage(response.history)
            raise APIExceptionSessionExpired("Access denied - request failed")
        PrintMessage(f"Platform Requests > '{method}:{response.url}'")
        return response

    def setRegulatoryCheckDetails(self, data):
        customerId = data["customerId"]
        PrintMessage(f"Customer Requests > set Regulatory details: '{customerId}'")
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/regulatorycheckdetails/put"

        customerIdStr = str(customerId).zfill(10)
        referer = f"https://slrebrandsyst.fnz.co.uk/wpadviser/en-gb/dashboard/home/main/customer/015-{customerIdStr}/detail/personal-details"
        return self.executeRequest("PUT", url, data=json.dumps(data), referer=referer)
