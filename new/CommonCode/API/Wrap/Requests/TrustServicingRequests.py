import json
import logging
from CommonCode.API.APIHelper import isResponseJSON
from CommonCode.API.Objects.Trust.TrustServicingModel import TrustServicingModel
from CommonCode.API.Wrap.Requests.PlatformRequests import PlatformRequests
from CommonCode.TestExecute.Logging import PrintMessage


class TrustServicingRequests(PlatformRequests):
    def getCustomerTrustServicingModel(self, customerId) -> TrustServicingModel:
        PrintMessage(f"TrustServicingRequests > getCustomerTrustServicingModel with customer Id: '{customerId}'", level=logging.DEBUG)
        params = {"customerId": customerId}
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/trustservicingmodel/get?customerId={customerId}"
        response = self.executeRequest("GET", url, params=params)
        if isResponseJSON(response):
            model = TrustServicingModel(response.json().get("Result", {}))
            model.currentTrustShare = self.getTrustShareData(customerId)
            return model

        PrintMessage("TrustServicingRequests Requests > getCustomerTrustServicingModel request failed", level=logging.DEBUG)
        PrintMessage(response, level=logging.DEBUG)
        return TrustServicingModel({})

    def getTrustShareData(self, customerId):
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/trustshare/get?customerId={customerId}"
        return self.executeRequest("GET", url).json().get("Result", {})

    def addBeneficiary(self, data):
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/trustmember/post"
        return self.executeRequest("POST", url, data=json.dumps(data))

    def deleteBeneficiary(self, data):
        url = f"{self.slWrapUrl}/wpadviser/en-gb/api/customer/trustmember/delete"
        return self.executeRequest("DELETE", url, data=json.dumps(data))
