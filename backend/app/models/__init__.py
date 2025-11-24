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

#from .user_models import user_roles_table, User, Role
from .user_models import user_roles_table, User
from .role import Role

from .document_library import DocumentLibrary, DocumentAuditLog

from .driving_license import (DriverLicenseOriginalRecord, DriverLicenseContact, DriverLicenseFictitiousTrap)

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
    "User",
    "Role",
    "user_roles_table",
    "DocumentLibrary",
    "DocumentAuditLog",
    "DriverLicenseOriginalRecord",
    "DriverLicenseContact",
    "DriverLicenseFictitiousTrap"
]
