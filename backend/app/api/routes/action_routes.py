from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.action_crud import perform_record_action, get_record_action_history
from app.schemas.action_schema import ActionRequest, ActionResponse, ActionLogOut

router = APIRouter(prefix="/actions", tags=["Record Actions"])

# main endpoint for performing actions on records
@router.post("/", response_model=ActionResponse)
def perform_action(
    action_data: ActionRequest, 
    request: Request,
    db: Session = Depends(get_db)
):

    try:
        # extract client IP address for audit logging
        client_ip = request.client.host
        
        # perform the action
        result = perform_record_action(db, action_data, client_ip)
        
        # return structured response
        return ActionResponse(
            success=True,
            message=f"Record {action_data.record_id} {action_data.action_type}d successfully",
            record_id=action_data.record_id,
            new_status=result["new_status"],
            action_logged=True,
            time_stamp=result["log_entry"].created_at
        )
        
    except ValueError as e:
        # handle business logic errors (invalid action, record not found, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error occurred : {str(e)}")

#history for a specific record
@router.get("/{record_id}/history", response_model=List[ActionLogOut])
def get_action_history(record_id: int, db: Session = Depends(get_db)):

    try:
        history = get_record_action_history(db, record_id)
        return [
            ActionLogOut(
                id=log.id,
                record_table=log.record_table,
                record_id=log.record_id,
                action_type_name=log.action_type.name,  # Join with ActionType
                user_id=log.user_id,
                notes=log.notes,
                created_at=log.created_at,
                ip_address=log.ip_address
            )
            for log in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve action history: ${e}")

# convenience endpoints for specific actions (optional but user-friendly)

#approve endpoint
@router.post("/{record_id}/approve")
def approve_record(record_id: int, request: Request, db: Session = Depends(get_db)):

    action_data = ActionRequest(
        record_id=record_id,
        record_table="vehicle_registration_master",
        action_type="approve",
        user_id=1,  #TODO: get from authentication laterrr
        notes="Approved via quick action"
    )
    return perform_action(action_data, request, db)

#reject endpoint
@router.post("/{record_id}/reject")
def reject_record(record_id: int, request: Request, db: Session = Depends(get_db)):

    action_data = ActionRequest(
        record_id=record_id,
        record_table="vehicle_registration_master", 
        action_type="reject",
        user_id=1,  # TODO: Get from authentication
        notes="Rejected via quick action"
    )
    return perform_action(action_data, request, db)

#hold endpoint
@router.post("/{record_id}/hold")
def hold_record(record_id: int, request: Request, db: Session = Depends(get_db)):

    action_data = ActionRequest(
        record_id=record_id,
        record_table="vehicle_registration_master",
        action_type="hold",
        user_id=1,  # TODO: Get from authentication
        notes="Put on hold via quick action"
    )
    return perform_action(action_data, request, db)
