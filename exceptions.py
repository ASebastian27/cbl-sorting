#exceptions.py

##Exceptions
class CapacityExceeded(Exception):
    "Raised when bin capacity was exceeded."
    pass
class BlockedCamException(Exception):
    "Raised when camera is possibly blocked."
    pass
class OverloadedCamException(Exception):
    "Raised when camera is possibly overloaded."
    pass
class UnknownWeightException(Exception):
    "Raised when a loadcell encountered an unknown weight."
    pass
class LostObjectException(Exception):
    "Raised when a loadcell encountered an unknown weight."
    pass
