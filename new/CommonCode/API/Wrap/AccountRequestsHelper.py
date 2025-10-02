from datetime import datetime, timedelta
from CommonCode.API.Wrap.PlatformRequestsHelper import PlatformRequestsHelper


class AccountRequestsHelper(PlatformRequestsHelper):
    DATE_FORMAT = "%Y-%m-%d"

    def getWPAccounts(self, inputString):
        accounts = self.platformRequests.customerSearchActorName(f"WP{inputString}")
        return [k for k in accounts if k.get("ClAccountId")]

    def getCustomer(self, customerId):
        self.platformRequests.getCustomerAccount(customerId)

    def getUsefullAccounts(self, instructions):
        return instructions

    def getProductValuationSummaryDetails(self, headHierarchy, subHierarchys):
        urlParamsStart = f"?headAccountHierarchyIds={headHierarchy}&"
        urlParamsEnd = f"&assetClassType=2&asAt={datetime.now().strftime(self.DATE_FORMAT)}T23%3A00%3A00.000Z"

        hierarchyIds = []
        for subHierarchy in subHierarchys:
            hierarchyIds.append(f"subAccountHierarchyIds={subHierarchy}")

        urlParamsMid = "&".join(hierarchyIds)
        return self.platformRequests.getProductValuationSummaryDetails(urlParamsStart + urlParamsMid + urlParamsEnd)

    def getPortFolioInvestment(self, subAccount):
        asAt = f"{(datetime.now()+timedelta(days=-1)).strftime(self.DATE_FORMAT)}T23%3A00%3A00.000Z"
        params = {
            "hierarchyIds": subAccount["SubAccountHierarchyId"],
            "assetClassType": 1,
            "asAt": asAt,
            "viewType": 0
        }
        return self.platformRequests.getPortFolioInvestment(params)
