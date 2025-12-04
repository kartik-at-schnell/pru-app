from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.record_suppression_schema import (
    SuppressRecordRequest,
    RevokeSuppressionRequest,
    RecordSuppressionResponse,
    SuppressionHistoryResponse,
    ActiveSuppressionsListAllResponse,
    SuppressSuccessResponse,
    RevokeSuccessResponse,
)
from app.crud.record_suppression_crud import (
    suppress_record,
    revoke_suppression,
    get_suppression_history,
    get_active_suppressions,
    is_record_suppressed,
    get_suppression_for_record,
)

router = APIRouter(
    prefix="/record-suppression",
    tags=["Record Suppression"],
    responses={
        404: {"description": "Resource not found"},
        400: {"description": "Bad request or invalid state"},
        500: {"description": "Internal server error"}
    }
)


# ============================================================================
# POST: SUPPRESS A RECORD
# ============================================================================

@router.post(
    "/suppress",
    response_model=SuppressSuccessResponse,
    summary="Suppress a record",
    description="Hide a record from normal searches. Creates audit trail entry.",
)
async def suppress_record_endpoint(
    payload: SuppressRecordRequest,
    db: Session = Depends(get_db)
):
    """
    Suppress (hide) a record.
    
    Supported record types:
    - vr_master: Vehicle Registration Master
    - vr_undercover: Vehicle Registration Undercover
    - vr_fictitious: Vehicle Registration Fictitious
    - dl_original: Driver License Original
    
    Example request:
    ```json
    {
      "record_type": "vr_master",
      "record_id": 123,
      "reason": "Undercover operation - high priority"
    }
    ```
    """
    try:
        suppression = suppress_record(db, payload)
        
        return SuppressSuccessResponse(
            suppression_id=suppression.id,
            record_type=suppression.record_type,
            record_id=suppression.record_id,
            status=suppression.status,
            suppressed_at=suppression.suppressed_at,
            message="Record suppressed successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error suppressing record: {str(e)}"
        )


# ============================================================================
# PUT: REVOKE SUPPRESSION (UNSUPPRESS)
# ============================================================================

@router.put(
    "/revoke/{suppression_id}",
    response_model=RevokeSuccessResponse,
    summary="Revoke a suppression",
    description="Unsuppress a record - make it visible again.",
)
async def revoke_suppression_endpoint(
    suppression_id: int,
    payload: RevokeSuppressionRequest,
    db: Session = Depends(get_db)
):
    """
    Revoke (unsuppress) a suppression request.
    
    This will:
    1. Mark the suppression as "revoked"
    2. Make the record visible again
    3. Log the revocation reason
    
    Example request:
    ```json
    {
      "revoke_reason": "Case closed - suspect captured"
    }
    ```
    """
    try:
        suppression = revoke_suppression(db, suppression_id, payload)
        
        return RevokeSuccessResponse(
            suppression_id=suppression.id,
            record_type=suppression.record_type,
            record_id=suppression.record_id,
            status=suppression.status,
            revoked_at=suppression.revoked_at,
            message="Suppression revoked - record now visible"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error revoking suppression: {str(e)}"
        )


# ============================================================================
# GET: SUPPRESSION HISTORY
# ============================================================================

@router.get(
    "/history/{record_type}/{record_id}",
    response_model=SuppressionHistoryResponse,
    summary="Get suppression history",
    description="View complete suppression history (active and revoked) for a record.",
)
async def get_history_endpoint(
    record_type: str,
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete suppression history for a record.
    
    Returns:
    - All suppressions (active and revoked)
    - Sorted by most recent first
    - Includes suppression and revocation reasons
    - Timestamps for all events
    
    Example path:
    `/record-suppression/history/vr_master/123`
    """
    try:
        history = get_suppression_history(db, record_type, record_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


# ============================================================================
# GET: LIST ALL ACTIVE SUPPRESSIONS
# ============================================================================

@router.get(
    "/list",
    response_model=ActiveSuppressionsListAllResponse,
    summary="List active suppressions",
    description="Get all records that are currently suppressed (hidden).",
)
async def list_active_suppressions_endpoint(
    record_type: str = Query(None, description="Filter by record type (optional)"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    List all currently active suppressions.
    
    Query parameters:
    - record_type (optional): Filter by type (vr_master, vr_undercover, etc)
    - limit: How many results to return (default 50, max 100)
    - offset: For pagination
    
    Example:
    `/record-suppression/list?record_type=vr_master&limit=50&offset=0`
    """
    try:
        result = get_active_suppressions(
            db,
            record_type=record_type,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing suppressions: {str(e)}"
        )


# ============================================================================
# GET: CHECK IF RECORD IS SUPPRESSED
# ============================================================================

@router.get(
    "/check/{record_type}/{record_id}",
    summary="Check suppression status",
    description="Check if a specific record is currently suppressed.",
)
async def check_suppression_endpoint(
    record_type: str,
    record_id: int,
    db: Session = Depends(get_db)
):
    try:
        suppression = get_suppression_for_record(db, record_type, record_id)
        
        if suppression:
            return {
                "is_suppressed": True,
                "suppression_id": suppression.id,
                "reason": suppression.reason,
                "suppressed_at": suppression.suppressed_at
            }
        else:
            return {
                "is_suppressed": False,
                "suppression_id": None,
                "reason": None
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking suppression: {str(e)}"
        )