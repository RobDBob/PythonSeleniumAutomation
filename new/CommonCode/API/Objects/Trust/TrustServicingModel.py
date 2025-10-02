from faker import Faker
from CommonCode.API.Objects.FromJsonModel import FromJsonModel
from CommonCode.API.Objects.Trust.OrganizationMemberModel import OrganizationMemberModel
from CommonCode.API.Objects.Trust.OrganizationModel import OrganizationModel
from CommonCode.API.Objects.Trust.TrustEnums import TrustRemoveReason, TrustRole
from CommonCode.TestHelpers.StringMethods import getFakeUKAddressAPI, getUniqueAlphaString


class TrustServicingModel(FromJsonModel):
    currentTrustShare: dict = {}

    def _getShareOfTrustItem(self, currentBeneficiary: OrganizationMemberModel, percentage):
        matches = [k for k in self.currentTrustShare if k["CustomerId"] == currentBeneficiary.customerId]
        if matches:
            matches[0]["Percentage"] = percentage
            return matches[0]
        return {
            "AccountId": self.sourceJson["HierarchyId"]["EntityId"],
            "AccountRoleType": 33,
            "AdditionalDataItemType": 4,
            "CustomerId": currentBeneficiary.customerId,
            "Percentage": percentage
        }

    def generateNewTrustBeneficiaryJson(self):
        """
        Creates beneficiary to be used in add beneficiary API request, gets data from organisation
        percentage = round(100 / (len(currentBeneficiaries) + 1), 2)
        """
        currentBeneficiaries = self.organization.getMembersByRelationship(TrustRole.Beneficiary)
        percentage = str(round(100 / (len(currentBeneficiaries) + 1), 2))
        dob = Faker().date_between("-50y", "-20y").strftime("%Y-%m-%d")
        breq = dict(self.organization.sourceJson)
        breq["OrganisationMembers"] = []
        breq["Beneficiaries"] = [{"Company": None,
                                  "Individual": {
                                      "ActorCategory": 2,
                                      "ActorOwnerId": self.organization.ownerAdviserId,
                                      "AddressDetails": [
                                          {
                                              "Address": getFakeUKAddressAPI(),
                                              "PhysicalAddressType": 1
                                          }
                                      ],
                                      "PersonalDetails": {
                                          "DateOfBirth": f"{dob}T00:00:00.000Z",
                                          "FamilyName": getUniqueAlphaString("autom_"),
                                          "Gender": 2,
                                          "GivenName": getUniqueAlphaString("autom_"),
                                          "MaritalStatus": 5,
                                          "Title": 1
                                      }
                                  },
                                  "Percentage": percentage,
                                  "Relationships": [
                                      TrustRole.Beneficiary.value
                                  ]
                                  }]
        breq["ShareOfTrustItem"] = [self._getShareOfTrustItem(k, percentage) for k in currentBeneficiaries]

        return {"organisation": breq}

    def generateRemoveTrustBeneficiaryJson(self, beneficiaryJsonToRemove):
        """
        TrustShare dict is used to retrieve correct AccountRoleType
        """
        currentBeneficiaries = self.organization.getMembersByRelationship(TrustRole.Beneficiary)
        percentage = str(round(100 / (len(currentBeneficiaries) - 1), 2)) if len(currentBeneficiaries) > 1 else 0

        customerIdToRemove = beneficiaryJsonToRemove["CustomerId"]
        breq = {"organisation": dict(self.organization.sourceJson)}
        breq["organisation"]["OrganisationMembers"] = []
        breq["organisation"]["Beneficiaries"] = [beneficiaryJsonToRemove]
        breq["organisation"]["ShareOfTrustItem"] = [self._getShareOfTrustItem(k, percentage) for k in currentBeneficiaries if k.customerId != customerIdToRemove]
        breq["organisation"]["ShareOfTrustToDelete"] = [self._getShareOfTrustItem(k, percentage) for k in currentBeneficiaries if k.customerId == customerIdToRemove][0]
        breq["deathTime"] = None
        breq["reasonType"] = TrustRemoveReason.Removed.value
        return breq

    @property
    def organization(self):
        return OrganizationModel(self._getValue("Organisation"))
