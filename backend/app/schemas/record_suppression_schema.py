from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from app.schemas.vehicle_registration_schema import MasterCreateRequest
from app.schemas.driving_license_schema import DriverLicenseOriginalCreate


class SuppressRecordRequest(BaseModel):
    reason: str = Field(..., min_length=2)

    class Config:
        from_attributes = True


class RevokeSuppressionRequest(BaseModel):
    revoke_reason: str = Field(..., min_length=5)

    class Config:
        from_attributes = True


class RecordSuppressionResponse(BaseModel):
    id: int
    record_type: str
    record_id: int
    reason: str
    suppressed_at: datetime
    status: str
    revoked_at: Optional[datetime] = None
    revoke_reason: Optional[str] = None

    class Config:
        from_attributes = True


class CheckSuppressionResponse(BaseModel):
    is_suppressed: bool
    suppression_id: Optional[int] = None
    reason: Optional[str] = None
    suppressed_at: Optional[datetime] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class SuppressionHistoryResponse(BaseModel):
    record_type: str
    record_id: int
    total_entries: int
    history: List[RecordSuppressionResponse]

    class Config:
        from_attributes = True


class ActiveSuppressionListResponse(BaseModel):
    suppression_id: int
    record_type: str
    record_id: int
    reason: str
    suppressed_at: datetime
    days_suppressed: int

    class Config:
        from_attributes = True


class ActiveSuppressionsListAllResponse(BaseModel):
    total_active: int
    suppressions: List[ActiveSuppressionListResponse]

    class Config:
        from_attributes = True


class SuppressSuccessResponse(BaseModel):
    suppression_id: int
    record_type: str
    record_id: int
    status: str
    suppressed_at: datetime
    message: str = "Record suppressed successfully"

    class Config:
        from_attributes = True


class RevokeSuccessResponse(BaseModel):
    suppression_id: int
    record_type: str
    record_id: int
    status: str
    revoked_at: datetime
    message: str = "Suppression revoked successfully"

    class Config:
        from_attributes = True


class CreateSuppressedVRMasterRequest(MasterCreateRequest):

    suppression_reason: Optional[str] = None

    class Config:
        from_attributes = True


class CreateSuppressedVRMasterResponse(BaseModel):
    record: dict
    suppression: dict
    message: str = "VRMaster created and suppressed successfully"

    class Config:
        from_attributes = True


class CreateSuppressedDLOriginalRequest(DriverLicenseOriginalCreate):
    
    suppression_reason: Optional[str] = None

    class Config:
        from_attributes = True


class CreateSuppressedDLOriginalResponse(BaseModel):
    record: dict
    suppression: dict
    message: str = "DriverLicense created and suppressed successfully"

    class Config:
        from_attributes = True