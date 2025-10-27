from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database  import get_db
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

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])

# CREATE route
@router.post("/", response_model=VehicleRegistrationMaster)
def create_vehicle(record: VehicleRegistrationMasterCreate, db: Session = Depends(get_db)):
    return create_vehicle_record(db, record)

# Read all
@router.get("/", response_model=List[VehicleRegistrationMaster])
def list_vehicles(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    db: Session = Depends(get_db)
):
    return get_all_vehicles(db, skip=skip, limit=limit, search=search)

# Read one
@router.get("/{record_id}", response_model=VehicleRegistrationMaster)
def get_vehicle(record_id: int, db: Session = Depends(get_db)):
    record = get_vehicle_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return record

# Update response_model and input schema
@router.put("/{record_id}", response_model=VehicleRegistrationMaster)
def update_vehicle(record_id: int, update_data: VehicleRegistrationMasterBase, db: Session = Depends(get_db)):
    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return updated

# delete
@router.delete("/{record_id}")
def delete_vehicle(record_id: int, db: Session = Depends(get_db)):
    deleted = delete_vehicle_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return {"message": f"Record ID {record_id} deleted successfully"}


# Details endpoint
@router.get("/{master_id}/details", response_model=VehicleRegistrationMasterDetails)
def get_master_record_details(master_id: int, db: Session = Depends(get_db)):
    
    db_record = get_vehicle_master_details(db=db, master_id=master_id)
    
    if db_record is None:
        raise HTTPException(status_code=404, detail="Vehicle Master Record not found")
        
    return db_record