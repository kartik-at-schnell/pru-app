from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class SuppressRecordRequest(BaseModel):
    """Request to suppress a record"""
    record_type: str = Field(..., description="Type of record: vr_master, vr_undercover, vr_fictitious, dl_original")
    record_id: int = Field(..., description="ID of the record to suppress")
    reason: str = Field(..., min_length=5, description="Reason for suppression")

    class Config:
        from_attributes = True
        examples = {
            "record_type": "vr_master",
            "record_id": 123,
            "reason": "Undercover operation - high priority"
        }


class RevokeSuppressionRequest(BaseModel):
    """Request to revoke (unsuppress) a suppression"""
    revoke_reason: str = Field(..., min_length=5, description="Reason for revoking suppression")

    class Config:
        from_attributes = True
        examples = {
            "revoke_reason": "Case closed - suspect captured"
        }


class RecordSuppressionResponse(BaseModel):
    """Response for a single suppression entry"""
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


class SuppressionHistoryResponse(BaseModel):
    """Complete suppression history for a record"""
    record_type: str
    record_id: int
    total_entries: int
    history: List[RecordSuppressionResponse]

    class Config:
        from_attributes = True


class ActiveSuppressionListResponse(BaseModel):
    """List of currently active (non-revoked) suppressions"""
    suppression_id: int
    record_type: str
    record_id: int
    reason: str
    suppressed_at: datetime
    days_suppressed: int

    class Config:
        from_attributes = True


class ActiveSuppressionsListAllResponse(BaseModel):
    """Response for listing all active suppressions"""
    total_active: int
    suppressions: List[ActiveSuppressionListResponse]

    class Config:
        from_attributes = True


class SuppressSuccessResponse(BaseModel):
    """Response when suppression is successful"""
    suppression_id: int
    record_type: str
    record_id: int
    status: str
    suppressed_at: datetime
    message: str = "Record suppressed successfully"

    class Config:
        from_attributes = True


class RevokeSuccessResponse(BaseModel):
    """Response when revocation is successful"""
    suppression_id: int
    record_type: str
    record_id: int
    status: str
    revoked_at: datetime
    message: str = "Suppression revoked - record now visible"

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    status_code: int
    error_type: str

    class Config:
        from_attributes = True