from enum import Enum


class TrustRole(Enum):
    Trustee = 1
    Unknown2 = 2
    Unknown3 = 3
    Unknown4 = 4
    Settlor = 5
    Beneficiary = 6


class TrustRemoveReason(Enum):
    Removed = 3
