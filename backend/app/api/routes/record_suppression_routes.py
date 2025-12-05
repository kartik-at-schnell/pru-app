from fastapi import APIRouter, Depends, HTTPException, Path, Query
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
    CheckSuppressionResponse,
    CreateSuppressedVRMasterRequest,
    CreateSuppressedDLOriginalRequest,
    CreateSuppressedVRMasterResponse,
    CreateSuppressedDLOriginalResponse
)
from app.crud.record_suppression_crud import (
    suppress_record,
    revoke_suppression,
    get_suppression_history,
    get_active_suppressions,
    is_record_suppressed,
    get_suppression_for_record,
    create_suppressed_vr_master,
    create_suppressed_dl_original
)
from app.crud.vehicle_registration_crud import get_vehicle_master_details
from app.models.record_suppression import RecordSuppressionRequest
from app.security import get_current_user

router = APIRouter(
    prefix="/record-suppression",
    tags=["Record Suppression"],
    responses={
        404: {"description": "Resource not found"},
        400: {"description": "Bad request or invalid state"},
        500: {"description": "Internal server error"}
    }
)

# suppress a rrecord
@router.post(
    "/suppress/{record_type}/{record_id}",
    response_model=SuppressSuccessResponse,
    status_code=201
)
async def suppress_record_endpoint(
    record_type: str,
    record_id: int,
    payload: SuppressRecordRequest,
    db: Session = Depends(get_db)
):
    try:
        suppression = suppress_record(db, record_type, record_id, payload)
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


@router.put(
    "/revoke/{suppression_id}",
    response_model=RevokeSuccessResponse,
    status_code=200
)
async def revoke_suppression_endpoint(
    suppression_id: int,
    payload: RevokeSuppressionRequest,
    db: Session = Depends(get_db)
):
    try:
        suppression = revoke_suppression(db, suppression_id, payload)
        return RevokeSuccessResponse(
            suppression_id=suppression.id,
            record_type=suppression.record_type,
            record_id=suppression.record_id,
            status=suppression.status,
            revoked_at=suppression.revoked_at,
            message="Suppression revoked successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error revoking suppression: {str(e)}"
        )


@router.get(
    "/history/{record_type}/{record_id}",
    response_model=SuppressionHistoryResponse,
    status_code=200
)
async def get_history_endpoint(
    record_type: str,
    record_id: int,
    db: Session = Depends(get_db)
):
    try:
        history = get_suppression_history(db, record_type, record_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@router.get(
    "/list",
    response_model=ActiveSuppressionsListAllResponse,
    status_code=200
)
async def list_active_suppressions_endpoint(
    record_type: str = Query(None, description="Filter by record type (optional)"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
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


@router.get(
    "/check/{record_type}/{record_id}",
    response_model=CheckSuppressionResponse,
    status_code=200
)
async def check_suppression_endpoint(
    record_type: str,
    record_id: int,
    db: Session = Depends(get_db)
):
    try:
        suppression = get_suppression_for_record(db, record_type, record_id)
        if suppression:
            return CheckSuppressionResponse(
                is_suppressed=True,
                suppression_id=suppression.id,
                reason=suppression.reason,
                suppressed_at=suppression.suppressed_at,
                status=suppression.status
            )
        else:
            return CheckSuppressionResponse(
                is_suppressed=False,
                suppression_id=None,
                reason=None,
                suppressed_at=None,
                status=None
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking suppression: {str(e)}"
        )


@router.post(
    "/create-suppressed/vr-master",
    response_model=CreateSuppressedVRMasterResponse,
    status_code=201
)
async def create_suppressed_vr_master_endpoint(
    payload: CreateSuppressedVRMasterRequest,
    db: Session = Depends(get_db)
):
    try:
        result = create_suppressed_vr_master(db, payload)
        return CreateSuppressedVRMasterResponse(
            record={
                "id": result["record"].id,
                "license_number": result["record"].license_number,
                "vehicle_id_number": result["record"].vehicle_id_number,
                "registered_owner": result["record"].registered_owner,
                "is_suppressed": result["record"].is_suppressed,
                "created_at": result["record"].created_at if hasattr(result["record"], 'created_at') else None
            },
            suppression={
                "suppression_id": result["suppression"].id,
                "record_type": result["suppression"].record_type,
                "record_id": result["suppression"].record_id,
                "reason": result["suppression"].reason,
                "status": result["suppression"].status,
                "suppressed_at": result["suppression"].suppressed_at
            },
            message="VRMaster created and suppressed successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating suppressed VRMaster: {str(e)}"
        )


@router.post(
    "/create-suppressed/dl-original",
    response_model=CreateSuppressedDLOriginalResponse,
    status_code=201
)
async def create_suppressed_dl_original_endpoint(
    payload: CreateSuppressedDLOriginalRequest,
    db: Session = Depends(get_db)
):
    try:
        result = create_suppressed_dl_original(db, payload)
        return CreateSuppressedDLOriginalResponse(
            record={
                "id": result["record"].id,
                "fdl": result["record"].fdl,
                "fln": result["record"].fln,
                "ffn": result["record"].ffn,
                "is_suppressed": result["record"].is_suppressed,
                "created_at": result["record"].created_at if hasattr(result["record"], 'created_at') else None
            },
            suppression={
                "suppression_id": result["suppression"].id,
                "record_type": result["suppression"].record_type,
                "record_id": result["suppression"].record_id,
                "reason": result["suppression"].reason,
                "status": result["suppression"].status,
                "suppressed_at": result["suppression"].suppressed_at
            },
            message="DriverLicense created and suppressed successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating suppressed DriverLicense: {str(e)}"
        )
    
@router.get("/{suppression_id}/detailed")
def open_suppressed_record(
    suppression_id: int = Path(..., description="Suppression numeric id"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # 1) load suppression row
    suppression = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.id == suppression_id
    ).first()
    if not suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")

    record_type = (suppression.record_type or "").lower()
    record_id = suppression.record_id

    # 2) dispatch to the correct detail fetcher
    if record_type == "vr_master":
        # returns full master + nested lists (contacts, uc, fc)
        record_detail = get_vehicle_master_details(db, master_id=record_id)
    elif record_type in ("vr_undercover", "vr_fictitious"):
        # you can call get_vehicle_master_details if you want parent + children,
        # or call specific UC/FC detail endpoints if you need only child record
        record_detail = db.query(...)  # or call your existing UC/FC getters
    elif record_type == "dl_original":
        record_detail = get_dl_detail(db, record_id=record_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported record_type {record_type}")

    # 3) return combined payload (or redirect/url)
    return {
        "suppression": RecordSuppressionResponse.model_validate(suppression),
        "record_type": record_type,
        "record_id": record_id,
        "record_detail": record_detail
    }