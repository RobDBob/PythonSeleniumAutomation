from datetime import datetime
from CommonCode.API.Objects.FromJsonModel import FromJsonModel


class CustomerObj(FromJsonModel):
    dateWSlashesFormat = "%d/%m/%Y"

    @property
    def customerId(self):
        return self._getValue("CustomerId")

    @property
    def customerRoleType(self):
        """
        Stored as "1"
        returned UI friendly as: ?
        """
        return self._getValue("CustomerRoleType")

    @property
    def customerStatus(self):
        """
        Stored as "2"
        returned UI friendly as: ?
        """
        return self._getValue("CustomerStatus")

    @property
    def dateCreated(self):
        return self._getValue("DateCreated")

    @property
    def dateOfBirth(self):
        """
        Stored as ISO format: "1994-06-11T00:00:00"
        Returned UI friendly as: 31/05/2023
        cheatsheet:
         - https://docs.python.org/3/library/datetime.html
         - https://strftime.org/
        """
        dateTime = datetime.fromisoformat(self._getValue("DateOfBirth"))
        return dateTime.strftime(CustomerObj.dateWSlashesFormat)

    @property
    def firstName(self):
        return self._getValue("FirstName")

    @property
    def isProspect(self):
        return self._getValue("IsProspect")

    @property
    def lastName(self):
        return self._getValue("LastName")

    @property
    def middleName(self):
        return self._getValue("MiddleName")

    @property
    def ownerAdviserName(self):
        return self._getValue("OwnerAdviserName")

    @property
    def title(self):
        return self._getValue("Title")
