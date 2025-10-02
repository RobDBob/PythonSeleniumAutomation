from CommonCode.API.Objects.FromJsonModel import FromJsonModel
from CommonCode.API.Objects.Trust.OrganizationMemberModel import OrganizationMemberModel
from CommonCode.API.Objects.Trust.TrustEnums import TrustRole


class OrganizationModel(FromJsonModel):
    def getAdditionalBeneficiaries(self) -> list[OrganizationMemberModel]:
        """
        additional beneficiaries
        roles includes 4
        actor category is 2
        """
        beneficiaries = self.getMembersByRelationship(TrustRole.Beneficiary)
        return [k for k in beneficiaries if k._getValue("Individual", {}).get("ActorCategory") == 2]

    def getMembersByRelationship(self, relationShip: TrustRole) -> list[OrganizationMemberModel]:
        return [k for k in self.members if relationShip in k.relationships]

    @property
    def members(self) -> list[OrganizationMemberModel]:
        return [OrganizationMemberModel(k) for k in self._getValue("OrganisationMembers")]

    @property
    def ownerAdviserId(self):
        return self._getValue("OwnerAdviserId")
