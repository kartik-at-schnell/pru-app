from .base import Base, BaseModel, ActionType, RecordActionLog
from .vehicle_registration import (
    VehicleRegistrationMaster,
    VehicleRegistrationUnderCover,
    VehicleRegistrationFictitious,
    VehicleRegistrationUnderCoverTrapInfo,
    VehicleRegistrationFictitiousTrapInfo,
    VehicleRegistrationContact,
    VehicleRegistrationReciprocalIssued,
    VehicleRegistrationReciprocalReceived
)

# export all models for easy importing
__all__ = [
    "Base",
    "BaseModel",
    "ActionType",
    "RecordActionLog",
    "VehicleRegistrationMaster",
    "VehicleRegistrationUnderCover",
    "VehicleRegistrationFictitious",
    "VehicleRegistrationUnderCoverTrapInfo",
    "VehicleRegistrationFictitiousTrapInfo",
    "VehicleRegistrationContact",
    "VehicleRegistrationReciprocalIssued",
    "VehicleRegistrationReciprocalReceived",
]
