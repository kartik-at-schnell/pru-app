from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import VehicleRegistrationMaster
from app.schemas.vehicle_registration_schema import(
    VehicleRegistrationCreate,
    VehicleRegistrationUpdate
)

#create op
def create_vehicle_record(db:Session, record_data: VehicleRegistrationCreate):
    new_record = VehicleRegistrationMaster(**record_data.model_dump())    #converts the Pydantic model instance into a dictionary
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
        query = query.filter(VehicleRegistrationMaster.license_number.ilike(f"%{search}"))  #only for searching by license no
        return query.offset(skip).limit(limit).all()

# update
def update_vehicle_record(db:Session, record_id: int, update_data: VehicleRegistrationUpdate):

    record = get_vehicle_by_id(db, record_id)

    if not record:
        return None
    
    for key, value in update_data.dict(exclude_unset = True).items():
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


