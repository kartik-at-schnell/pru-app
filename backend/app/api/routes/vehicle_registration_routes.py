from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud.vehicle_registration_crud import (
    create_vehicle_record,
    get_all_vehicles,
    get_vehicle_by_id,
    update_vehicle_record,
    delete_vehicle_record,
    get_vehicle_master_details
)

from app.schemas.vehicle_registration_schema import(
    VehicleRegistrationMasterCreate,
    VehicleRegistrationMasterBase,
    VehicleRegistrationMaster,
    VehicleRegistrationMasterDetails
)

from app.schemas.base_schema import ApiResponse

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])

# CREATE route
@router.post("/", response_model=ApiResponse[VehicleRegistrationMaster], status_code=status.HTTP_201_CREATED)
def create_vehicle(record: VehicleRegistrationMasterCreate, db: Session = Depends(get_db)):
    # Simple wrapper for success
    try:
        new_record = create_vehicle_record(db, record)
        return ApiResponse[VehicleRegistrationMaster](data=new_record, message="Record created successfully")
    except Exception as e: # Basic error catch
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create record: {e}")

# Read all
@router.get("/", response_model=ApiResponse[List[VehicleRegistrationMaster]])
def list_vehicles(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    db: Session = Depends(get_db)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, search=search)
        return ApiResponse[List[VehicleRegistrationMaster]](data=vehicle_list)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve records")

# Read one
@router.get("/{record_id}", response_model=ApiResponse[VehicleRegistrationMaster])
def get_vehicle(record_id: str, db: Session = Depends(get_db)):
    record = get_vehicle_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return ApiResponse[VehicleRegistrationMaster](data=record)

@router.put("/{record_id}", response_model=ApiResponse[VehicleRegistrationMaster])
def update_vehicle(record_id: str, update_data: VehicleRegistrationMasterBase, db: Session = Depends(get_db)):
    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return ApiResponse[VehicleRegistrationMaster](data=updated, message="Record updated successfully")

# delete
@router.delete("/{record_id}", response_model=ApiResponse)
def delete_vehicle(record_id: str, db: Session = Depends(get_db)):
    deleted = delete_vehicle_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return ApiResponse(message=f"Record ID {record_id} deleted successfully")

# Details endpoint
@router.get("/{master_id}/details", response_model=ApiResponse[VehicleRegistrationMasterDetails])
def get_master_record_details(master_id: str, db: Session = Depends(get_db)):
    db_record = get_vehicle_master_details(db=db, master_id=master_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Vehicle Master Record not found")
    return ApiResponse[VehicleRegistrationMasterDetails](data=db_record)
