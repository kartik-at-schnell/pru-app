from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import vehicle_registration, user_models
from app.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

#provides a summary of record statuses
@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        # query to count records grouped by status
        summary = (
            db.query(
                vehicle_registration.VehicleRegistrationMaster.approval_status,
                func.count(vehicle_registration.VehicleRegistrationMaster.id).label("count"),
            )
            .group_by(vehicle_registration.VehicleRegistrationMaster.approval_status)
            .all()
        )
        #convert the list of tuples to a dictionary
        summary_dict = {status: count for status, count in summary}
        return summary_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard summary: {e}")
    