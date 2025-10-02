from CommonCode.API.Objects.FromJsonModel import FromJsonModel
from CommonCode.API.Objects.Trust.TrustEnums import TrustRole


class OrganizationMemberModel(FromJsonModel):
    @property
    def customerId(self):
        return self._getValue("CustomerId")

    @property
    def actorCategory(self):
        return

    @property
    def relationships(self):
        return [TrustRole(k) for k in self._getValue("Relationships")]
