from CommonCode.Models.AdvisorChargesObj import AdvisorChargesObj
from CommonCode.Models.BaseDataObj import BaseDataObj
from CommonCode.Models.InvestmentsObj import InvestmentsObj
from CommonCode.Models.PaymentDataObj import PaymentDataObj
from TestPages import DataEnums


class ProductDataObj(BaseDataObj):
    def getPaymentMethod(self, paymentType):
        matchedPaymentTypeData = [k for k in self.dataDict.get(DataEnums.PAYMENTS_IN, "") if k.get(DataEnums.PAYMENT_TYPE) == paymentType]
        if not matchedPaymentTypeData:
            return PaymentDataObj({})

        return PaymentDataObj(matchedPaymentTypeData[0])

    @property
    def adviserCharges(self):
        return AdvisorChargesObj(self.dataDict.get(DataEnums.ADVISOR_CHARGES, {}))

    @property
    def investments(self):
        return InvestmentsObj(self.dataDict.get(DataEnums.INVESTMENTS, {}))
