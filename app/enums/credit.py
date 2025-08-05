from enum import Enum

class CreditOriginEnum(str, Enum):
    PLAN = "PLAN"
    CREDIT = "CREDIT"
    PAYMENT = "PAYMENT"
    BONUS = "BONUS"