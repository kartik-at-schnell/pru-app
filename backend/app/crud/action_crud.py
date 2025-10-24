from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from app.models import VehicleRegistrationMaster, RecordActionLog, ActionType
from app.schemas.action_schema import ActionRequest

def get_action_type_by_name(db: Session, action_name: str):

    return db.query(ActionType).filter(ActionType.name == action_name).first()

def get_record_by_id(db: Session, record_id: int):

    return db.query(VehicleRegistrationMaster).filter(
        VehicleRegistrationMaster.id == record_id
    ).first()

def perform_record_action(
    db: Session, 
    action_data: ActionRequest, 
    ip_address: Optional[str] = None
):
    
    record = get_record_by_id(db, action_data.record_id)
    if not record:
        raise ValueError(f"Record with ID {action_data.record_id} not found")
    
    action_type = get_action_type_by_name(db, action_data.action_type)
    if not action_type:
        raise ValueError(f"Invalid action type: {action_data.action_type}") #for logging purpose
    
    current_status = record.approval_status
    if action_data.action_type == "approve" and current_status == "approved":
        raise ValueError("Record is already approved")
    elif action_data.action_type == "reject" and current_status == "rejected":
        raise ValueError("Record is already rejected")
    
    old_status = record.approval_status  # for logging
    
    if action_data.action_type == "approve":
        record.approval_status = "approved"
    elif action_data.action_type == "reject":
        record.approval_status = "rejected"
    elif action_data.action_type == "hold":
        record.approval_status = "on_hold"
    elif action_data.action_type == "reprocess":
        record.approval_status = "pending"
    else:
        raise ValueError(f"Unsupported action: {action_data.action_type}")
    

    log_entry = RecordActionLog(
        record_table=action_data.record_table,
        record_id=action_data.record_id,
        action_type_id=action_type.id,           # fk to ActionType
        user_id=action_data.user_id,
        notes=action_data.notes,
        created_at=func.now(),
        ip_address=ip_address or "unknown"
    )
    
    db.add(log_entry)
    db.add(record)          
    db.commit()                 
    db.refresh(record)          
    db.refresh(log_entry)       
    
    return {
        "record": record,
        "log_entry": log_entry,
        "old_status": old_status,
        "new_status": record.approval_status
    }

def get_record_action_history(db: Session, record_id: int):

    return db.query(RecordActionLog).join(ActionType).filter(
        RecordActionLog.record_id == record_id,
        RecordActionLog.record_table == "vehicle_registration_master"
    ).order_by(RecordActionLog.created_at.desc()).all()

