from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.record_suppression import RecordSuppressionRequest
from app.schemas.record_suppression_schema import (
    SuppressRecordRequest,
    RevokeSuppressionRequest,
    RecordSuppressionResponse,
    SuppressionHistoryResponse,
    ActiveSuppressionListResponse,
    ActiveSuppressionsListAllResponse,
)


# ============================================================================
# SUPPRESS A RECORD
# ============================================================================

def suppress_record(
    db: Session,
    payload: SuppressRecordRequest
) -> RecordSuppressionRequest:
    """
    Suppress a record and create audit trail entry.
    
    Steps:
    1. Verify record exists and is not already suppressed
    2. Create RecordSuppressionRequest entry (status: active)
    3. Mark the actual record as is_suppressed=TRUE
    
    Args:
        db: Database session
        payload: SuppressRecordRequest with record_type, record_id, reason
        
    Returns:
        RecordSuppressionRequest: The created suppression entry
        
    Raises:
        HTTPException 404: Record not found
        HTTPException 400: Record already suppressed
    """
    
    # Verify record exists and check if already suppressed
    record = _get_record_by_type(db, payload.record_type, payload.record_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Record {payload.record_type}#{payload.record_id} not found"
        )
    
    # Check if already suppressed
    if hasattr(record, 'is_suppressed') and record.is_suppressed:
        raise HTTPException(
            status_code=400,
            detail=f"Record {payload.record_type}#{payload.record_id} is already suppressed"
        )
    
    # Create suppression request entry
    suppression = RecordSuppressionRequest(
        record_type=payload.record_type,
        record_id=payload.record_id,
        reason=payload.reason,
        suppressed_at=datetime.utcnow(),
        status="active",
        revoked_at=None,
        revoke_reason=None
    )
    
    db.add(suppression)
    db.flush()  # Get the ID before commit
    
    # Mark the actual record as suppressed
    record.is_suppressed = True
    
    db.commit()
    db.refresh(suppression)
    
    return suppression


# ============================================================================
# REVOKE SUPPRESSION (UNSUPPRESS)
# ============================================================================

def revoke_suppression(
    db: Session,
    suppression_id: int,
    payload: RevokeSuppressionRequest
) -> RecordSuppressionRequest:
    """
    Revoke (unsuppress) a suppression request.
    
    Steps:
    1. Find the suppression request
    2. Verify it's not already revoked
    3. Update suppression status to "revoked" with timestamp and reason
    4. Mark the actual record as is_suppressed=FALSE
    
    Args:
        db: Database session
        suppression_id: ID of the RecordSuppressionRequest
        payload: RevokeSuppressionRequest with revoke_reason
        
    Returns:
        RecordSuppressionRequest: Updated suppression entry
        
    Raises:
        HTTPException 404: Suppression not found
        HTTPException 400: Already revoked
    """
    
    # Find suppression request
    suppression = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.id == suppression_id
    ).first()
    
    if not suppression:
        raise HTTPException(
            status_code=404,
            detail=f"Suppression request #{suppression_id} not found"
        )
    
    # Check if already revoked
    if suppression.status == "revoked":
        raise HTTPException(
            status_code=400,
            detail=f"Suppression request #{suppression_id} is already revoked"
        )
    
    # Find the actual record and unsuppress it
    record = _get_record_by_type(db, suppression.record_type, suppression.record_id)
    if record and hasattr(record, 'is_suppressed'):
        record.is_suppressed = False
    
    # Update suppression request
    suppression.status = "revoked"
    suppression.revoked_at = datetime.utcnow()
    suppression.revoke_reason = payload.revoke_reason
    
    db.commit()
    db.refresh(suppression)
    
    return suppression


# ============================================================================
# GET SUPPRESSION HISTORY
# ============================================================================

def get_suppression_history(
    db: Session,
    record_type: str,
    record_id: int
) -> SuppressionHistoryResponse:
    """
    Get complete suppression history for a record.
    
    Returns all suppression entries (active AND revoked) for this record,
    ordered newest first.
    
    Args:
        db: Database session
        record_type: Type of record (vr_master, vr_undercover, etc)
        record_id: ID of the record
        
    Returns:
        SuppressionHistoryResponse: Complete history
    """
    
    entries = db.query(RecordSuppressionRequest).filter(
        and_(
            RecordSuppressionRequest.record_type == record_type,
            RecordSuppressionRequest.record_id == record_id
        )
    ).order_by(RecordSuppressionRequest.suppressed_at.desc()).all()
    
    history = [RecordSuppressionResponse.from_orm(entry) for entry in entries]
    
    return SuppressionHistoryResponse(
        record_type=record_type,
        record_id=record_id,
        total_entries=len(history),
        history=history
    )


# ============================================================================
# GET ALL ACTIVE SUPPRESSIONS
# ============================================================================

def get_active_suppressions(
    db: Session,
    record_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> ActiveSuppressionsListAllResponse:
    """
    Get list of all currently active (non-revoked) suppressions.
    
    Args:
        db: Database session
        record_type: Filter by type (optional)
        limit: Number of results to return
        offset: Pagination offset
        
    Returns:
        ActiveSuppressionsListAllResponse: List of active suppressions
    """
    
    query = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.status == "active"
    )
    
    if record_type:
        query = query.filter(RecordSuppressionRequest.record_type == record_type)
    
    total = query.count()
    
    entries = query.order_by(
        RecordSuppressionRequest.suppressed_at.desc()
    ).offset(offset).limit(limit).all()
    
    suppressions = []
    for entry in entries:
        days_suppressed = (datetime.utcnow() - entry.suppressed_at.replace(tzinfo=None)).days
        suppressions.append(ActiveSuppressionListResponse(
            suppression_id=entry.id,
            record_type=entry.record_type,
            record_id=entry.record_id,
            reason=entry.reason,
            suppressed_at=entry.suppressed_at,
            days_suppressed=days_suppressed
        ))
    
    return ActiveSuppressionsListAllResponse(
        total_active=total,
        suppressions=suppressions
    )


# ============================================================================
# SEARCH WITH SUPPRESSION FILTER
# ============================================================================

def is_record_suppressed(
    db: Session,
    record_type: str,
    record_id: int
) -> bool:
    """
    Check if a record is currently suppressed.
    
    Args:
        db: Database session
        record_type: Type of record
        record_id: ID of record
        
    Returns:
        bool: True if suppressed, False otherwise
    """
    
    suppression = db.query(RecordSuppressionRequest).filter(
        and_(
            RecordSuppressionRequest.record_type == record_type,
            RecordSuppressionRequest.record_id == record_id,
            RecordSuppressionRequest.status == "active"
        )
    ).first()
    
    return suppression is not None


def get_suppression_for_record(
    db: Session,
    record_type: str,
    record_id: int
) -> Optional[RecordSuppressionRequest]:
    """
    Get current active suppression for a record (if any).
    
    Args:
        db: Database session
        record_type: Type of record
        record_id: ID of record
        
    Returns:
        RecordSuppressionRequest or None
    """
    
    return db.query(RecordSuppressionRequest).filter(
        and_(
            RecordSuppressionRequest.record_type == record_type,
            RecordSuppressionRequest.record_id == record_id,
            RecordSuppressionRequest.status == "active"
        )
    ).first()


# ============================================================================
# HELPER FUNCTION: GET RECORD BY TYPE
# ============================================================================

def _get_record_by_type(db: Session, record_type: str, record_id: int):
    """
    Helper function to get a record by its type and ID.
    
    Args:
        db: Database session
        record_type: Type of record (vr_master, vr_undercover, vr_fictitious, dl_original)
        record_id: ID of the record
        
    Returns:
        The record object or None if not found
    """
    
    if record_type == "vr_master":
        from app.models.vehicle_registration import VehicleRegistrationMaster
        return db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id == record_id
        ).first()
    
    elif record_type == "vr_undercover":
        from app.models.vehicle_registration import VehicleRegistrationUnderCover
        return db.query(VehicleRegistrationUnderCover).filter(
            VehicleRegistrationUnderCover.id == record_id
        ).first()
    
    elif record_type == "vr_fictitious":
        from app.models.vehicle_registration import VehicleRegistrationFictitious
        return db.query(VehicleRegistrationFictitious).filter(
            VehicleRegistrationFictitious.id == record_id
        ).first()
    
    elif record_type == "dl_original":
        from app.models.driving_license import DriverLicenseOriginalRecord
        return db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id == record_id
        ).first()
    
    else:
        return None