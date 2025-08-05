from enum import Enum

class CompanyStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"
    
class CompanyOpenEnum(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
