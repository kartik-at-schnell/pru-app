from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional
from app.models import VehicleRegistrationMaster, RecordActionLog, ActionType, user_models
from app.schemas.action_schema import ActionRequest
from app.models import user_models
from app.models.driving_license import DriverLicenseOriginalRecord

def get_action_type_by_name(db: Session, action_name: str):
    return db.query(ActionType).filter(ActionType.name == action_name).first()

def get_record_by_id(db: Session, record_id: str):
    return db.query(VehicleRegistrationMaster).filter(
        VehicleRegistrationMaster.id == record_id
    ).first()

def perform_record_action(
    db: Session,
    action_data: ActionRequest,
    current_user: user_models.User,
    ip_address: Optional[str] = None
):
    record = get_record_by_id(db, action_data.record_id)
    if not record:
        raise ValueError(f"Record with ID {action_data.record_id} not found")
    action_type = get_action_type_by_name(db, action_data.action_type)
    if not action_type:
        raise ValueError(f"Invalid action type: {action_data.action_type}")
    current_status = record.approval_status
    # check to prevent redundant actions
    if action_data.action_type == "approve" and current_status == "approved":
        raise ValueError("Record is already approved")
    elif action_data.action_type == "reject" and current_status == "rejected":
        raise ValueError("Record is already rejected")
    elif action_data.action_type == "hold" and current_status == "on_hold":
        raise ValueError("Record is already on hold")
    old_status = record.approval_status #for logging
    # Update status based on action_type
    if action_data.action_type == "approve":
        record.approval_status = "approved"
    elif action_data.action_type == "reject":
        record.approval_status = "rejected"
    elif action_data.action_type == "hold":
        record.approval_status = "on_hold"
    elif action_data.action_type == "reprocess": # not working rn
        record.approval_status = "pending"
    else:
        raise ValueError(f"Unsupported action type: {action_data.action_type}")
    # create the log entry using the authenticated user's ID
    log_entry = RecordActionLog(
        record_type=action_data.record_table,
        record_id=action_data.record_id,
        action_type_id=action_type.id,
        user_id=str(current_user.id), #use the ID from the token/dependency
        notes=action_data.notes,
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

# get hitory
def get_record_action_history(db: Session, record_id: str):
    return db.query(RecordActionLog).join(ActionType).filter(
        RecordActionLog.record_id == record_id,
        RecordActionLog.record_table == "vehicle_registration_master"
    ).order_by(RecordActionLog.created_at.desc()).all()

# DL FUNCTIONS

# get by id
def get_dl_record_by_id(db: Session, record_id: int):
    return db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).first()

def perform_dl_record_action(
    db: Session,
    record_id: int,
    action_type_name: str,
    current_user: user_models.User,
    notes: Optional[str] = None,
    ip_address: Optional[str] = None
):
    # get record
    record = get_dl_record_by_id(db, record_id)
    if not record:
        raise ValueError(f"Driver license record with ID {record_id} not found")

    # get action
    action_type = get_action_type_by_name(db, action_type_name)
    if not action_type:
        raise ValueError(f"Invalid action type: {action_type_name}")

    current_status = record.approval_status

    # redundant action prevention
    if action_type_name == "approve" and current_status == "approved":
        raise ValueError("Record is already approved")
    elif action_type_name == "reject" and current_status == "rejected":
        raise ValueError("Record is already rejected")
    elif action_type_name == "hold" and current_status == "on_hold":
        raise ValueError("Record is already on hold")

    old_status = record.approval_status

    # update status based on action_type
    if action_type_name == "approve":
        record.approval_status = "approved"
    elif action_type_name == "reject":
        record.approval_status = "rejected"
    elif action_type_name == "hold":
        record.approval_status = "on_hold"
    elif action_type_name == "reprocess":
        record.approval_status = "pending"
    else:
        raise ValueError(f"Unsupported action type: {action_type_name}")

    # log entry
    log_entry = RecordActionLog(
    record_type="driver_license_original",
    record_id=record_id,
    action_type_id=action_type.id,
    user_id=str(current_user.id),
    notes=notes,
    timestamp=datetime.now(timezone.utc),
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

#action history for dl
def get_dl_record_action_history(db: Session, record_id: int):
    return db.query(RecordActionLog).join(ActionType).filter(
        RecordActionLog.record_id == record_id,
        RecordActionLog.record_type == "driver_license_original"
    ).order_by(RecordActionLog.timestamp.desc()).all()
