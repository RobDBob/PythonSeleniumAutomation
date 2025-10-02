from CommonCode.Models.BaseDataObj import BaseDataObj
from TestPages import DataEnums, PageEnums


class AdvisorChargesObj(BaseDataObj):
    @property
    def iacType(self):
        return self.dataDict.get(DataEnums.IAC_CHARGE_TYPE)

    @property
    def iacTypeSymbol(self):
        if self.iacType == PageEnums.TYPE_PERCENTAGE:
            return "%"
        return str()

    @property
    def iacAmount(self):
        return self.dataDict.get(DataEnums.IAC_CHARGE_AMOUNT)

    @property
    def oacType(self):
        return self.dataDict.get(DataEnums.OAC_CHARGE_TYPE)

    @property
    def oacTypeSymbol(self):
        if self.oacType == PageEnums.TYPE_PERCENTAGE:
            return "%"
        return str()

    @property
    def oacAmount(self):
        return self.dataDict.get(DataEnums.OAC_CHARGE_AMOUNT)

    @property
    def oacFrequency(self):
        return self.dataDict.get(DataEnums.OAC_CHARGE_FREQUENCY)
