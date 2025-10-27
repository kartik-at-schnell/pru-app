from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

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

from app.schemas.vehicle_registration_schema import(
    VehicleRegistrationMasterCreate,  
    VehicleRegistrationMasterBase     
)

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
    
    return query.offset(skip).limit(limit).all()

# update
def update_vehicle_record(db:Session, record_id: int, update_data: VehicleRegistrationMasterBase):

    record = get_vehicle_by_id(db, record_id)

    if not record:
        return None
    
    for key, value in update_data.model_dump(exclude_unset = True).items():
        setattr(record, key, value)

    db.add(record)
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