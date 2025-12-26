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
    approve_suppression_request,
    reject_suppression_request,
    submit_suppression_request,
    suppress_record,
    revoke_suppression,
    get_suppression_history,
    get_active_suppressions,
    is_record_suppressed,
    get_suppression_for_record,
    create_suppressed_vr_master,
    create_suppressed_dl_original
)
from app.crud.vehicle_registration_crud import create_master_record, get_vehicle_master_details
from app.models.record_suppression import RecordSuppressionRequest
from app.security import get_current_user
from app.crud.action_crud import get_record_by_id
from app.models import user_models
from app.rbac import PermissionChecker, RoleChecker
from app.crud.driving_license_crud import create_original_record
from app.schemas.vehicle_registration_schema import MasterCreateRequest

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
# @router.post(
#     "/suppress/{record_type}/{record_id}",
#     response_model=SuppressSuccessResponse,
#     status_code=201
# )
# async def suppress_record_endpoint(
#     record_type: str,
#     record_id: int,
#     payload: SuppressRecordRequest,
#     db: Session = Depends(get_db),
#     current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
#     permission_check = Depends(PermissionChecker("suppression:submit"))
# ):
#     try:
#         suppression = suppress_record(db, record_type, record_id, payload)
#         return SuppressSuccessResponse(
#             suppression_id=suppression.id,
#             record_type=suppression.record_type,
#             record_id=suppression.record_id,
#             status=suppression.status,
#             suppressed_at=suppression.suppressed_at,
#             message="Record suppressed successfully"
#         )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error suppressing record: {str(e)}"
#         )

@router.post("/suppress/{record_type}/{record_id}", status_code=201)
async def suppress_record_endpoint(
    record_type: str,
    record_id: int,
    payload: SuppressRecordRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:submit"))
):
    try:
        result = submit_suppression_request(
            db,
            record_type=record_type,
            record_id=record_id,
            suppression_reason=payload.reason,
            requested_by=current_user.full_name or current_user.username,
            confidentiality_level=getattr(payload, 'confidentiality_level', None),
            notes_for_reviewer=getattr(payload, 'suppression_justification', None),
            requestor_email=getattr(payload, 'requestor_email', None),
            requestor_phone=getattr(payload, 'requestor_phone', None),
            department=getattr(payload, 'department', None),
            assigned_unit=getattr(payload, 'assigned_unit', None),
        )
        return {
            "request_id": result.id,
            "record_type": result.record_type,
            "record_id": result.record_id,
            "approval_status": "pending",
            "message": "Suppression request submitted. Awaiting approval."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting suppression request: {str(e)}")


@router.put(
    "/revoke/{suppression_id}",
    response_model=RevokeSuccessResponse,
    status_code=200
)
async def revoke_suppression_endpoint(
    suppression_id: int,
    payload: RevokeSuppressionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("suppression:edit"))
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
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:audit_view"))
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
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:view_list"))
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
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:view_details"))
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


# @router.post(
#     "/create-suppressed/vr-master",
#     response_model=CreateSuppressedVRMasterResponse,
#     status_code=201
# )
# async def create_suppressed_vr_master_endpoint(
#     payload: CreateSuppressedVRMasterRequest,
#     db: Session = Depends(get_db),
#     current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
#     permission_check = Depends(PermissionChecker("suppression:submit"))
# ):
#     try:
#         result = create_suppressed_vr_master(db, payload)
#         return CreateSuppressedVRMasterResponse(
#             record={
#                 "id": result["record"].id,
#                 "license_number": result["record"].license_number,
#                 "vehicle_id_number": result["record"].vehicle_id_number,
#                 "registered_owner": result["record"].registered_owner,
#                 "is_suppressed": result["record"].is_suppressed,
#                 "created_at": result["record"].created_at if hasattr(result["record"], 'created_at') else None
#             },
#             suppression={
#                 "suppression_id": result["suppression"].id,
#                 "record_type": result["suppression"].record_type,
#                 "record_id": result["suppression"].record_id,
#                 "reason": result["suppression"].reason,
#                 "status": result["suppression"].status,
#                 "suppressed_at": result["suppression"].suppressed_at
#             },
#             message="VRMaster created and suppressed successfully"
#         )
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error creating suppressed VRMaster: {str(e)}"
#         )

@router.post("/create-suppressed/vr-master", status_code=201)
async def create_suppressed_vr_master_endpoint(
    payload: CreateSuppressedVRMasterRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:submit"))
):
    try:
        from app.crud.vehicle_registration_crud import create_master_record
        
        record = create_master_record(db, payload)
        
        request = submit_suppression_request(
            db,
            record_type="vr_master",
            record_id=record.id,
            suppression_reason=payload.suppression_reason or payload.reason,
            requested_by=current_user.full_name or current_user.username,
            confidentiality_level=getattr(payload, 'confidentiality_level', None),
            notes_for_reviewer=getattr(payload, 'notes_for_reviewer', None),
            requestor_email=getattr(payload, 'requestor_email', None),
            requestor_phone=getattr(payload, 'requestor_phone', None),
            department=getattr(payload, 'department', None),
            assigned_unit=getattr(payload, 'assigned_unit', None),
        )
        
        return {
            "record": {
                "id": record.id,
                "license_number": record.license_number,
                "vehicle_id_number": record.vehicle_id_number,
                "registered_owner": record.registered_owner,
                "is_suppressed": record.is_suppressed,
                "created_at": record.created_at if hasattr(record, 'created_at') else None
            },
            "request": {
                "request_id": request.id,
                "record_type": request.record_type,
                "record_id": request.record_id,
                "approval_status": "pending",
                "created_at": request.created_at
            },
            "message": "VRMaster created. Suppression request pending approval."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating VRMaster: {str(e)}")

@router.post("/create-suppressed/dl-original", status_code=201)
async def create_suppressed_dl_original_endpoint(
    payload: CreateSuppressedDLOriginalRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:submit"))
):
    try:
        from app.crud.driving_license_crud import create_original_record
        
        record = create_original_record(db, payload)
        
        request = submit_suppression_request(
            db,
            record_type="dl_original",
            record_id=record.id,
            suppression_reason=payload.suppression_reason or payload.reason,
            requested_by=current_user.full_name or current_user.username,
            confidentiality_level=getattr(payload, 'confidentiality_level', None),
            notes_for_reviewer=getattr(payload, 'notes_for_reviewer', None),
            requestor_email=getattr(payload, 'requestor_email', None),
            requestor_phone=getattr(payload, 'requestor_phone', None),
            department=getattr(payload, 'department', None),
            assigned_unit=getattr(payload, 'assigned_unit', None),
        )
        
        return {
            "record": {
                "id": record.id,
                "fdl": record.fdl,
                "fln": record.fln,
                "ffn": record.ffn,
                "is_suppressed": record.is_suppressed,
                "created_at": record.created_at if hasattr(record, 'created_at') else None
            },
            "request": {
                "request_id": request.id,
                "record_type": request.record_type,
                "record_id": request.record_id,
                "approval_status": "pending",
                "created_at": request.created_at
            },
            "message": "DriverLicense created. Suppression request pending approval."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating DriverLicense: {str(e)}")
    
@router.get("/{suppression_id}/detailed")
def open_suppressed_record(
    suppression_id: int = Path(..., description="Suppression numeric id"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("suppression:view_details"))
):
    #load suppression row
    suppression = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.id == suppression_id
    ).first()
    if not suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")

    record_type = (suppression.record_type or "").lower()
    record_id = suppression.record_id


    if record_type == "vr_master":
        record_detail = get_vehicle_master_details(db, master_id=record_id)

    elif record_type in ("vr_undercover", "vr_fictitious"):
        record_detail = db.query(...)

    elif record_type == "dl_original":
        record_detail = get_record_by_id(db, record_id=record_id)

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported record_type {record_type}")

    # 3) return combined payload (or redirect/url)
    return {
        "suppression": RecordSuppressionResponse.model_validate(suppression),
        "record_type": record_type,
        "record_id": record_id,
        "record_detail": record_detail
    }

@router.post("/request/submit", status_code=201)
async def submit_suppression_request_endpoint(
    record_type: str = Query(..., description="vr_master, dl_original, etc."),
    record_id: int = Query(..., description="ID of record to suppress"),
    suppression_reason: str = Query(..., description="Reason for suppression"),
    confidentiality_level: str = Query(None, description="CONFIDENTIAL, RESTRICTED, etc."),
    notes_for_reviewer: str = Query(None, description="Notes for approver"),
    requestor_email: str = Query(None),
    requestor_phone: str = Query(None),
    department: str = Query(None),
    assigned_unit: str = Query(None),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    try:
        result = submit_suppression_request(
            db,
            record_type=record_type,
            record_id=record_id,
            suppression_reason=suppression_reason,
            requested_by=current_user.full_name or current_user.username,
            confidentiality_level=confidentiality_level,
            notes_for_reviewer=notes_for_reviewer,
            requestor_email=requestor_email,
            requestor_phone=requestor_phone,
            department=department,
            assigned_unit=assigned_unit,
        )
        return {
            "request_id": result.id,
            "record_type": result.record_type,
            "record_id": result.record_id,
            "approval_status": "pending",
            "message": "Suppression request submitted. Awaiting approval."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/request/pending", status_code=200)
async def list_pending_requests_endpoint(
    record_type: str = Query(None, description="Filter by record type (optional)"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(
        RoleChecker(["Admin", "Supervisor", "Manager"])
    ),
):
    try:
        from datetime import datetime
        from app.models.record_suppression import RecordSuppressionRequest
        
        query = db.query(RecordSuppressionRequest).filter(
            RecordSuppressionRequest.approval_status == "pending"
        )
        
        if record_type:
            query = query.filter(RecordSuppressionRequest.record_type == record_type)
        
        total_pending = query.count()
        
        requests = query.order_by(
            RecordSuppressionRequest.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        pending_list = []
        for req in requests:
            # Calculate days pending
            days_pending = (datetime.utcnow() - req.created_at.replace(tzinfo=None)).days
            
            pending_list.append({
                "request_id": req.id,
                "record_type": req.record_type,
                "record_id": req.record_id,
                "suppression_reason": req.suppression_reason,
                "requested_by": req.requested_by,
                "requested_at": req.created_at,
                "days_pending": days_pending,
                "confidentiality_level": req.confidentiality_level,
                "department": req.department,
                "assigned_unit": req.assigned_unit,
                "notes_for_reviewer": getattr(req, 'notes_for_reviewer', None),
            })
        
        return {
            "total_pending": total_pending,
            "returned_count": len(pending_list),
            "pending_requests": pending_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing pending requests: {str(e)}")



# Approval endpoints

@router.post("/request/{request_id}/approve", status_code=200)
async def approve_suppression_request_endpoint(
    request_id: int = Path(..., description="ID of suppression request"),
    comments: str = Query(None, description="Approval comments"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(
        RoleChecker(["Admin", "Supervisor"])
    ),
):
    try:
        result = approve_suppression_request(
            db,
            request_id=request_id,
            approved_by=current_user.full_name or current_user.username,
            comments=comments,
        )
        return {
            "request_id": result.id,
            "record_type": result.record_type,
            "record_id": result.record_id,
            "approval_status": "approved",
            "is_suppressed": True,
            "approved_at": result.approved_at,
            "approved_by": result.approved_by,
            "message": "Request approved. Record is now suppressed."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# reject endpoint

@router.post("/request/{request_id}/reject", status_code=200)
async def reject_suppression_request_endpoint(
    request_id: int = Path(..., description="ID of suppression request"),
    comments: str = Query(None, description="Rejection reason/comments"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(
        RoleChecker(["Admin", "Supervisor"])
    ),
):
    try:
        result = reject_suppression_request(
            db,
            request_id=request_id,
            rejected_by=current_user.full_name or current_user.username,
            comments=comments,
        )
        return {
            "request_id": result.id,
            "record_type": result.record_type,
            "record_id": result.record_id,
            "approval_status": "rejected",
            "is_suppressed": False,
            "rejected_at": result.approved_at,
            "rejected_by": result.approved_by,
            "message": "Request rejected. No action taken."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
