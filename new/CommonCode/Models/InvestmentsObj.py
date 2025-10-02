from CommonCode.Models.BaseDataObj import BaseDataObj
from CommonCode.Models.InvestmentAllocationObj import InvestmentAllocationObj
from TestPages import DataEnums


class InvestmentsObj(BaseDataObj):
    def getAllocation(self, investmentName):
        matchingAllocation = [k for k in self.dataDict.get(DataEnums.ALLOCATIONS) if k.get(DataEnums.INVESTMENT_NAME, "") == investmentName]
        if matchingAllocation:
            return matchingAllocation[0]
        return str()

    @property
    def distributionOption(self):
        return self.dataDict.get(DataEnums.DISTRIBUTION_OPTION, "")

    @property
    def allocations(self):
        return [InvestmentAllocationObj(k) for k in self.dataDict.get(DataEnums.ALLOCATIONS)]
