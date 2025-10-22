from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import VehicleRegistrationMaster, RecordActionLog, ActionType

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

#summary statistics
@router.get("/summary")
def get_system_summary(db: Session = Depends(get_db)):

    
    #count records by status
    status_counts = db.query(
        VehicleRegistrationMaster.approval_status,
        func.count(VehicleRegistrationMaster.id).label('count')
    ).group_by(VehicleRegistrationMaster.approval_status).all()
    
    #convert to dictionary for easier frontend consumption
    status_breakdown = {status: count for status, count in status_counts}
    
    #total record count
    total_records = db.query(VehicleRegistrationMaster).count()
    
    # recent activity (last 10 actions)
    recent_actions = db.query(RecordActionLog).join(ActionType).order_by(
        RecordActionLog.created_at.desc()
    ).limit(10).all()
    
    #count actions by type today
    from datetime import datetime, date
    today = date.today()
    daily_actions = db.query(
        ActionType.name,
        func.count(RecordActionLog.id).label('count')
    ).join(RecordActionLog).filter(
        func.date(RecordActionLog.created_at) == today
    ).group_by(ActionType.name).all()
    
    daily_breakdown = {action: count for action, count in daily_actions}
    
    return {
        "total_records": total_records,
        "status_breakdown": status_breakdown,
        "daily_actions": daily_breakdown,
        "recent_activity": [
            {
                "id": action.id,
                "action_type": action.action_type.name,
                "record_id": action.record_id,
                "user_id": action.user_id,
                "timestamp": action.created_at,
                "notes": action.notes
            }
            for action in recent_actions
        ]
    }

#endpoint to get count of pending records, maybe i could use it for notification count
@router.get("/pending-count")
def get_pending_count(db: Session = Depends(get_db)):

    pending_count = db.query(VehicleRegistrationMaster).filter(
        VehicleRegistrationMaster.approval_status == "pending"
    ).count()
    
    return {"pending_records": pending_count}
