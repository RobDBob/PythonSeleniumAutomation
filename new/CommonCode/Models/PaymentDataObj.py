from CommonCode.Models.BaseDataObj import BaseDataObj
from CommonCode.TestHelpers.StringMethods import formatNumberAsCurrency
from TestPages import DataEnums


class PaymentDataObj(BaseDataObj):
    @property
    def type(self):
        return self._data.get(DataEnums.PAYMENT_TYPE)

    @property
    def contributor(self):
        return self._data.get(DataEnums.CONTRIBUTOR)

    @property
    def amount(self):
        return formatNumberAsCurrency(self._data.get(DataEnums.AMOUNT, -1))

    @property
    def method(self):
        return self._data.get(DataEnums.PAYMENT_METHOD)
