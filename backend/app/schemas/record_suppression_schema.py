from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from app.schemas.vehicle_registration_schema import MasterCreateRequest
from app.schemas.driving_license_schema import DriverLicenseOriginalCreate


class SuppressRecordRequest(BaseModel):
    reason: str = Field(..., min_length=2)

    owner_name: Optional[str] = None
    suppression_justification: Optional[str] = None
    confidentiality_level: Optional[str] = None
    requested_by: Optional[str] = None
    requestor_email: Optional[str] = None
    requestor_phone: Optional[str] = None
    department: Optional[str] = None
    assigned_unit: Optional[str] = None

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

    suppression_request_id: Optional[str] = None
    owner_name: Optional[str] = None
    suppression_reason: Optional[str] = None
    suppression_justification: Optional[str] = None
    confidentiality_level: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes_for_reviewer: Optional[str] = None
    attachment_files: Optional[str] = None
    requested_by: Optional[str] = None
    requestor_email: Optional[str] = None
    requestor_phone: Optional[str] = None
    department: Optional[str] = None
    assigned_unit: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    audit_log_reference_id: Optional[str] = None

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
    owner_name: Optional[str] = None
    confidentiality_level: Optional[str] = None
    assigned_unit: Optional[str] = None
    status: str    

    record_detail: Optional[dict] = None

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

    suppression_reason: Optional[str] = Field(None, description="Primary reason for suppression")
    owner_name: Optional[str] = Field(None, description="Name of the record owner")
    suppression_justification: Optional[str] = Field(None, description="Legal/policy justification")
    confidentiality_level: Optional[str] = Field(None, description="Classification (CONFIDENTIAL, RESTRICTED)")
    effective_date: Optional[date] = Field(None, description="When suppression starts")
    expiry_date: Optional[date] = Field(None, description="When suppression expires")
    notes_for_reviewer: Optional[str] = Field(None, description="Internal notes")
    attachment_files: Optional[str] = Field(None, description="Comma-separated file names")
    requested_by: Optional[str] = Field(None, description="Who requested suppression")
    requestor_email: Optional[str] = Field(None, description="Requestor email")
    requestor_phone: Optional[str] = Field(None, description="Requestor phone")
    department: Optional[str] = Field(None, description="Department making request")
    assigned_unit: Optional[str] = Field(None, description="Unit responsible")
    suppression_request_id: Optional[str] = Field(None, description="Suppression request ID")
    audit_log_reference_id: Optional[str] = Field(None, description="Audit log reference")


    class Config:
        from_attributes = True


class CreateSuppressedVRMasterResponse(BaseModel):
    record: dict
    suppression: dict
    message: str = "VRMaster created and suppressed successfully"

    class Config:
        from_attributes = True


class CreateSuppressedDLOriginalRequest(DriverLicenseOriginalCreate):
    
    suppression_reason: Optional[str] = Field(None, description="Primary reason for suppression")
    owner_name: Optional[str] = Field(None, description="Name of the record owner")
    suppression_justification: Optional[str] = Field(None, description="Legal/policy justification")
    confidentiality_level: Optional[str] = Field(None, description="Classification (CONFIDENTIAL, RESTRICTED)")
    effective_date: Optional[date] = Field(None, description="When suppression starts")
    expiry_date: Optional[date] = Field(None, description="When suppression expires")
    notes_for_reviewer: Optional[str] = Field(None, description="Internal notes")
    attachment_files: Optional[str] = Field(None, description="Comma-separated file names")
    requested_by: Optional[str] = Field(None, description="Who requested suppression")
    requestor_email: Optional[str] = Field(None, description="Requestor email")
    requestor_phone: Optional[str] = Field(None, description="Requestor phone")
    department: Optional[str] = Field(None, description="Department making request")
    assigned_unit: Optional[str] = Field(None, description="Unit responsible")
    suppression_request_id: Optional[str] = Field(None, description="Suppression request ID")
    audit_log_reference_id: Optional[str] = Field(None, description="Audit log reference")

    class Config:
        from_attributes = True


class CreateSuppressedDLOriginalResponse(BaseModel):
    record: dict
    suppression: dict
    message: str = "DriverLicense created and suppressed successfully"

    class Config:
        from_attributes = True