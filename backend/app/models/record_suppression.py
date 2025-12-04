from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from .base import BaseModel

# audit trail for tracking suppression reqs
class RecordSuppressionRequest(BaseModel):
    __tablename__ = "record_suppression_requests"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    
    record_type = Column(String(50), nullable=False, index=True)
    
    record_id = Column(Integer, nullable=False, index=True)
    
    reason = Column(Text, nullable=False)
    
    suppressed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    status = Column(String(20), default="active", nullable=False, index=True)
    
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    revoke_reason = Column(Text, nullable=True)
    
    def __repr__(self):
        return (
            f"<RecordSuppressionRequest(id={self.id}, record_type={self.record_type}, "
            f"record_id={self.record_id}, status={self.status})>"
        )