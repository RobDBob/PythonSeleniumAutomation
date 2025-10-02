from enum import Enum


class OrderEnum(Enum):
    PRE_POOLED = "Pre-Pooled"
    POOLED = "Pooled"
    PLACED = "Placed"
    AUTHORISED = "Authorised"
    AUTHORISED_SWITCH = "AuthorisedSwitch"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
