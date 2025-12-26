from sqlalchemy import JSON, Column, Date, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from .base import BaseModel

# extra fields for suppression
class RecordSuppressionRequest(BaseModel):
    __tablename__ = "record_suppression_requests"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    record_type = Column(String(50), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    reason = Column(Text, nullable=False)
    suppressed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoke_reason = Column(Text, nullable=True)
    suppression_reason = Column(Text, nullable=True)
    suppression_justification = Column(Text, nullable=True)
    
    suppression_request_id = Column(String(100), nullable=True, unique=True)
    owner_name = Column(String(255), nullable=True)
    
    confidentiality_level = Column(String(50), nullable=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    notes_for_reviewer = Column(Text, nullable=True)
    attachment_files = Column(String(500), nullable=True)
    requested_by = Column(String(255), nullable=True)
    requestor_email = Column(String(255), nullable=True)
    requestor_phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    assigned_unit = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    updated_by = Column(String(100), nullable=True)
    audit_log_reference_id = Column(String(100), nullable=True)
    approval_status = Column(String(20), default="pending", nullable=False, index=True)  # pending, approved, rejected
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_comments = Column(Text, nullable=True)  # ppproval/rejection comments
    payload = Column(JSON, nullable=True)  # to tore full request payload if needed
    payload_type = Column(String(50), nullable=True)
    
    def __repr__(self):
        return (
            f"<RecordSuppressionRequest("
            f"id={self.id}, "
            f"record_type={self.record_type}, "
            f"status={self.status}, "
            f"approval_status={self.approval_status})>"
        )
    