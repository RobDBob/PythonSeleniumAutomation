from CommonCode.Models.BaseDataObj import BaseDataObj
from TestPages import DataEnums


class InvestmentAllocationObj(BaseDataObj):
    @property
    def name(self):
        return self.dataDict.get(DataEnums.INVESTMENT_NAME, "")

    @property
    def allocationPercentage(self):
        return self.dataDict.get(DataEnums.ALLOCATION_PERCENTAGE, "")

    @property
    def allocationFieldName(self):
        return self.dataDict.get(DataEnums.ALLOCATION_FIELD_NAME, "")
