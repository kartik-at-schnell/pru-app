from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.action_crud import (
    perform_record_action, 
    get_record_action_history,
    perform_dl_record_action,
    get_dl_record_action_history
)
from app.schemas.action_schema import ActionRequest, ActionResponse, ActionLogOut
from app.database import get_db
from app.models import user_models
from app.security import get_current_user
from app.crud.vehicle_registration_crud import bulk_active, bulk_approve, bulk_inactive, bulk_reject, bulk_set_on_hold, mark_active, mark_inactive
from app.schemas.base_schema import ApiResponse
from app.schemas.vehicle_registration_schema import BulkActionRequest, BulkActionResponse
from app.models.driving_license import DriverLicenseOriginalRecord

router = APIRouter(prefix="/actions", tags=["Record Actions"])

# main endpoint for performing actions on records
@router.post("/", response_model=ActionResponse)
def perform_action(
    action_data: ActionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        # extract client IP address for audit logging
        client_ip = request.client.host
        # perform the action
        result = perform_record_action(db, action_data, current_user, client_ip)
        # return structured response
        return ActionResponse(
            success=True,
            message=f"Record {action_data.record_id} {action_data.action_type}d successfully",
            record_id=action_data.record_id,
            new_status=result["new_status"],
            action_logged=True,
            time_stamp=result["log_entry"].timestamp
        )
    except ValueError as e:
        # handle business logic errors (invalid action, record not found, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error occurred : {str(e)}")

#history for a specific record
@router.get("/{record_id}/history", response_model=List[ActionLogOut])
def get_action_history(record_id: str,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)):
    try:
        history = get_record_action_history(db, record_id)
        return [
            ActionLogOut(
                id=log.id,
                record_table=log.record_type,
                record_id=log.record_id,
                action_type_name=log.action_type.name, # Join with ActionType
                user_id=log.user_id,
                notes=log.notes,
                created_at=log.timestamp,
                ip_address=log.ip_address
            )
            for log in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve action history: ${e}")

# convenience endpoints for specific actions (optional but user-friendly)
#approve endpoint
@router.post("/{record_id}/approve")
def approve_record(record_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)):
    action_data = ActionRequest(
        record_id=record_id,
        record_table="vehicle_registration_master",
        action_type="approve",
        notes="Approved via quick action"
    )
    return perform_action(action_data, request, db, current_user)

#reject endpoint
@router.post("/{record_id}/reject")
def reject_record(record_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)):
    action_data = ActionRequest(
        record_id=record_id,
        record_table="vehicle_registration_master",
        action_type="reject",
        notes="Rejected via quick action"
    )
    return perform_action(action_data, request, db, current_user)

#hold endpoint
@router.post("/{record_id}/hold")
def hold_record(record_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)):
    action_data = ActionRequest(
        record_id=record_id,
        record_table="vehicle_registration_master",
        action_type="hold",
        notes="Put on hold via quick action"
    )
    return perform_action(action_data, request, db, current_user)

# mark inactive
@router.post("/{record_id}/inactive")
async def mark_inactive_route(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = mark_inactive(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"status": "marked inactive", "record_id": record_id}

# mark active
@router.post("/{record_id}/active")
async def mark_active_route(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = mark_active(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"status": "marked active", "record_id": record_id}

# DRIVER LICENSE ACTIONS

# DL approve endpoint
@router.post("/dl/{record_id}/approve", response_model=ApiResponse)
def approve_dl_record(
    record_id: int,
    request: Request,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        client_ip = request.client.host
        result = perform_dl_record_action(
            db=db,
            record_id=record_id,
            action_type_name="approve",
            current_user=current_user,
            notes=notes or "Approved via actions API",
            ip_address=client_ip
        )
        return ApiResponse(
            status="success",
            message=f"Driver license record {record_id} approved successfully",
            data={
                "record_id": record_id,
                "old_status": result["old_status"],
                "new_status": result["new_status"],
                "timestamp": result["log_entry"].timestamp
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# DL reject endpoint
@router.post("/dl/{record_id}/reject", response_model=ApiResponse)
def reject_dl_record(
    record_id: int,
    request: Request,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        client_ip = request.client.host
        result = perform_dl_record_action(
            db=db,
            record_id=record_id,
            action_type_name="reject",
            current_user=current_user,
            notes=notes or "Rejected via actions API",
            ip_address=client_ip
        )
        return ApiResponse(
            status="success",
            message=f"Driver license record {record_id} rejected successfully",
            data={
                "record_id": record_id,
                "old_status": result["old_status"],
                "new_status": result["new_status"],
                "timestamp": result["log_entry"].timestamp
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# DL hold endpoint
@router.post("/dl/{record_id}/hold", response_model=ApiResponse)
def hold_dl_record(
    record_id: int,
    request: Request,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        client_ip = request.client.host
        result = perform_dl_record_action(
            db=db,
            record_id=record_id,
            action_type_name="hold",
            current_user=current_user,
            notes=notes or "Put on hold via actions API",
            ip_address=client_ip
        )
        return ApiResponse(
            status="success",
            message=f"Driver license record {record_id} set on hold successfully",
            data={
                "record_id": record_id,
                "old_status": result["old_status"],
                "new_status": result["new_status"],
                "timestamp": result["log_entry"].timestamp
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# DL action history
@router.get("/dl/{record_id}/history", response_model=List[ActionLogOut])
def get_dl_action_history(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        history = get_dl_record_action_history(db, record_id)
        return [
            ActionLogOut(
                id=log.id,
                record_table=log.record_type,
                record_id=log.record_id,
                action_type_name=log.action_type.name,
                user_id=log.user_id,
                notes=log.notes,
                created_at=log.timestamp,
                ip_address=log.ip_address
            )
            for log in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve DL action history: {str(e)}")


# bulk actions routes

#bulk approve
@router.post("/bulk-approve", response_model=ApiResponse[BulkActionResponse])
def bulk_approve_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_approve(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully approved {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

# bulk reject
@router.post("/bulk-reject", response_model=ApiResponse[BulkActionResponse])
def bulk_reject_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_reject(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully rejected {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

# bulk on-hold
@router.post("/bulk-on-hold", response_model=ApiResponse[BulkActionResponse])
def bulk_on_hold_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_set_on_hold(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully set {updated_count} records to on-hold"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

#bulk flag active
@router.post("/bulk-active", response_model=ApiResponse[BulkActionResponse])
def bulk_active_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_active(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully activated {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

 # bulk flag inactive
@router.post("/bulk-inactive", response_model=ApiResponse[BulkActionResponse])
def bulk_inactive_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_inactive(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully deactivated {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

# separate routes for DL for now

# bulk approve
def bulk_dl_approve(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id.in_(record_ids),
            DriverLicenseOriginalRecord.approval_status != "approved"
        ).update(
            {"approval_status": "approved"},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk approve failed: {str(e)}")

# bulk reject
def bulk_dl_reject(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id.in_(record_ids),
            DriverLicenseOriginalRecord.approval_status != "rejected"
        ).update(
            {"approval_status": "rejected"},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk reject failed: {str(e)}")

# on_hold
def bulk_dl_set_on_hold(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id.in_(record_ids),
            DriverLicenseOriginalRecord.approval_status != "on_hold"
        ).update(
            {"approval_status": "on_hold"},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk on-hold failed: {str(e)}")

# activate
def bulk_dl_active(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id.in_(record_ids),
            DriverLicenseOriginalRecord.active_status == False
        ).update(
            {"active_status": True},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk activate failed: {str(e)}")

# bulk deactivate
def bulk_dl_inactive(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id.in_(record_ids),
            DriverLicenseOriginalRecord.active_status == True
        ).update(
            {"active_status": False},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk deactivate failed: {str(e)}")
