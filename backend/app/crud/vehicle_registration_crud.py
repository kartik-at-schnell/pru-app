# FILE: app/crud/vehicle_registration_crud.py

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

# --- Import all the models we need ---
# (This part of your file was already correct)
from app.models import (
    VehicleRegistrationMaster, 
    VehicleRegistrationFictitious, 
    VehicleRegistrationUnderCover,
    VehicleRegistrationContact,
    VehicleRegistrationReciprocalIssued,
    VehicleRegistrationReciprocalReceived,
    VehicleRegistrationUnderCoverTrapInfo,
    VehicleRegistrationFictitiousTrapInfo
)

# --- 1. THE IMPORT FIX ---
# We are now importing the NEW schema names that
# actually exist in your vehicle_registration_schema.py file
from app.schemas.vehicle_registration_schema import(
    VehicleRegistrationMasterCreate,  # <-- Was VehicleRegistrationCreate
    VehicleRegistrationMasterBase     # <-- We'll use this for updates
)

# --- 2. THE FUNCTION SIGNATURE FIX ---
# We change 'VehicleRegistrationCreate' to 'VehicleRegistrationMasterCreate'
def create_vehicle_record(db:Session, record_data: VehicleRegistrationMasterCreate):
    new_record = VehicleRegistrationMaster(**record_data.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

#read op

#get by id
def get_vehicle_by_id(db: Session, record_id: int):
    return db.query(VehicleRegistrationMaster).filter(VehicleRegistrationMaster.id== record_id).first()

#get all, this is for search bar
def get_all_vehicles(db: Session, skip:int= 0, limit:int = 30, search: Optional[str] = None):

    query = db.query(VehicleRegistrationMaster)
    if search:
        query = query.filter(VehicleRegistrationMaster.license_number.ilike(f"%{search}"))
    
    # I also fixed the bug from your file where this line was missing
    # so pagination works even without a search.
    return query.offset(skip).limit(limit).all()

# --- 3. THE FUNCTION SIGNATURE FIX ---
# We change 'VehicleRegistrationUpdate' to 'VehicleRegistrationMasterBase'
def update_vehicle_record(db:Session, record_id: int, update_data: VehicleRegistrationMasterBase):

    record = get_vehicle_by_id(db, record_id)

    if not record:
        return None
    
    # 'model_dump()' is the correct new Pydantic method
    for key, value in update_data.model_dump(exclude_unset = True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

#delete
def delete_vehicle_record(db:Session, record_id: int):
    
    record = get_vehicle_by_id(db, record_id)

    if not record:
        return None
    
    db.delete(record)
    db.commit()

    return record

# function to get all the details for one vehicle
# (This is the function we added before, it is correct)
def get_vehicle_master_details(db: Session, master_id: int):
    
    query = (
        db.query(VehicleRegistrationMaster)
        .filter(VehicleRegistrationMaster.id == master_id)
        .options(
            
            joinedload(VehicleRegistrationMaster.contacts),
            joinedload(VehicleRegistrationMaster.reciprocal_issued),
            joinedload(VehicleRegistrationMaster.reciprocal_received),
            
            joinedload(VehicleRegistrationMaster.undercover_records)
            .subqueryload(VehicleRegistrationUnderCover.trap_info),
            
            joinedload(VehicleRegistrationMaster.fictitious_records)
            .subqueryload(VehicleRegistrationFictitious.trap_info)
        )
    )
    
    return query.first()