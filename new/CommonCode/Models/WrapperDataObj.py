from CommonCode.Models.BaseDataObj import BaseDataObj
from TestPages import DataEnums, PageEnums


class WrapperDataObj(BaseDataObj):
    @property
    def financialAdvice(self):
        return self._data.get(DataEnums.FINANCIAL_ADVICE, PageEnums.NO)

    @property
    def paperlessPreference(self):
        return self._data.get(DataEnums.PAPERLESS_PREFERENCE, PageEnums.NO)
