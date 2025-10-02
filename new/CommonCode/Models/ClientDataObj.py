import datetime
from CommonCode.Models.BaseDataObj import BaseDataObj
from TestPages import DataEnums, PageEnums


class ClientDataObj(BaseDataObj):
    DOB_FORMAT = "%d/%m/%Y"

    def __init__(self, clientDetails: dict, fullClientDetails: dict):
        super().__init__({**clientDetails, **fullClientDetails})

    @property
    def title(self):
        return self._data[DataEnums.TITLE]

    @property
    def fullName(self):
        return f"{self._data[DataEnums.FIRST_NAME]} {self._data[DataEnums.SURNAME]}"

    @property
    def gender(self):
        return self._data[DataEnums.GENDER]

    @property
    def dob(self):
        date = self._data[DataEnums.DOB]
        if isinstance(date, (datetime.datetime, datetime.date)):
            return date.strftime(self.DOB_FORMAT)
        return date

    @property
    def nin(self):
        return self._data[DataEnums.NATIONAL_INSURANCE_NUMBER]

    @property
    def primaryNationality(self):
        for nationalityDict in self._data[DataEnums.NATIONALITIES]:
            if nationalityDict.get(DataEnums.CLIENT_PRIMARY_CITIZENSHIP, "").lower() in PageEnums.YES_CHOICE:
                return f"{nationalityDict.get(DataEnums.NATIONALITY)} only"
        return str()

    @property
    def taxResidencyOutsideUK(self):
        if self._data[DataEnums.TAX_RESIDENCY_OUTSIDE_UK] in PageEnums.NO_CHOICE:
            return "UK only"
        return str()
