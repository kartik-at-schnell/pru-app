from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


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


class CreateSuppressedVRMasterRequest(BaseModel):
    license_number: str
    vehicle_id_number: str
    registered_owner: str
    address: str
    city: str
    state: str = "California"
    zip_code: str
    make: str
    model: str
    year_model: int
    body_type: Optional[str] = None
    type_license: Optional[str] = None
    type_vehicle: Optional[str] = None
    category: Optional[str] = None
    expiration_date: Optional[date] = None
    date_issued: Optional[date] = None
    date_received: Optional[date] = None
    date_fee_received: Optional[date] = None
    amount_paid: Optional[Decimal] = None
    amount_due: Optional[Decimal] = None
    amount_received: Optional[Decimal] = None
    use_tax: Optional[Decimal] = None
    sticker_issued: Optional[str] = None
    sticker_numbers: Optional[str] = None
    cert_type: Optional[str] = None
    mp: Optional[str] = None
    mo: Optional[str] = None
    axl: Optional[str] = None
    wc: Optional[str] = None
    cc_alco: Optional[str] = None
    active_status: Optional[bool] = True
    suppression_reason: Optional[str] = None

    class Config:
        from_attributes = True


class CreateSuppressedVRMasterResponse(BaseModel):
    record: dict
    suppression: dict
    message: str = "VRMaster created and suppressed successfully"

    class Config:
        from_attributes = True


class CreateSuppressedDLOriginalRequest(BaseModel):
    tln: str
    tfn: str
    tdl: str
    fln: str
    ffn: str
    fdl: str
    agency: Optional[str] = None
    contact: Optional[str] = None
    date_issued: Optional[date] = None
    modified: Optional[datetime] = None
    approval_status: Optional[str] = "pending"
    active_status: Optional[bool] = True
    suppression_reason: Optional[str] = None

    class Config:
        from_attributes = True


class CreateSuppressedDLOriginalResponse(BaseModel):
    record: dict
    suppression: dict
    message: str = "DriverLicense created and suppressed successfully"

    class Config:
        from_attributes = True