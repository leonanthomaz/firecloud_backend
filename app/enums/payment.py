from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PREPAID = "PREPAID"
    OVERDUE = "OVERDUE"
    TRIAL = "TRIAL"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    
class PaymentType(str, Enum):
    PLAN = "PLAN"
    CREDIT = "CREDIT"
    PREPAID = "PREPAID"
    TRIAL = "TRIAL"
    
class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    PIX = "PIX"
    BOLETO = "BOLETO"
    PAYPAL = "PAYPAL"
    TRANSFER = "TRANSFER"

