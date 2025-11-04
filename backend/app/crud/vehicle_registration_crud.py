from fastapi import HTTPException
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

def create_vehicle_record(db:Session, record_data: VehicleRegistrationMasterCreate, record_type: Optional[str] = "master"):

    if record_type == "undercover":
        model_class = VehicleRegistrationUnderCover
    elif record_type == "fictitious":
        model_class = VehicleRegistrationFictitious
    else:  # default master
        model_class = VehicleRegistrationMaster

    new_record = model_class(**record_data.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

#read op

#get by id
def get_vehicle_by_id(db: Session, record_id: int):
    return db.query(VehicleRegistrationMaster).filter(VehicleRegistrationMaster.id== record_id).first()

#get all, this is for search bar
def get_all_vehicles(db: Session,
                     skip:int= 0,
                     limit:int = 10,
                     approval_status: Optional[str] = None,
                     search: Optional[str] = None,
                     record_type: Optional[str]= "master"):
    # decide which table to query based on record_type parameter
    if record_type == "undercover":
        model = VehicleRegistrationUnderCover
    elif record_type == "fictitious":
        model = VehicleRegistrationFictitious
    else:  # default to master if no type specified
        model = VehicleRegistrationMaster

    query = db.query(model)

    if approval_status:
        query = query.filter(VehicleRegistrationMaster.approval_status == approval_status)

    if search:
        query = query.filter(model.license_number.ilike(f"%{search}"))
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

# mark record inactive
def mark_inactive(db, record_id: int):
    record = db.query(VehicleRegistrationMaster).get(record_id)
    if(record):
        record.active_status = False
        db.commit()
        return record
    
    return None

#mark active
def mark_active(db, record_id: int):
    record = get_vehicle_by_id(db, record_id)

    if(record):
        record.active_status = True
        db.commit()
        return record
    return None

# function to get all the details for one vehicle
def get_vehicle_master_details(db: Session, master_id: str):
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

#helper function to validate master exists and return it
def get_master_by_id(db: Session, master_id: str):
    master = db.query(VehicleRegistrationMaster).filter(
        VehicleRegistrationMaster.id == master_id
    ).first()
    if not master:
        raise HTTPException(status_code=404, detail=f"Master record {master_id} not found")
    return master

#dropdown to get all master ids
def get_all_masters_for_dropdown(db: Session):
    return db.query(
        VehicleRegistrationMaster.id, 
        VehicleRegistrationMaster.vehicle_id_number,
        VehicleRegistrationMaster.registered_owner
    ).filter(
        VehicleRegistrationMaster.active_status == True  # Only active masters
    ).all()

# create uc with masters , auto-fetched

def create_undercover(db: Session, master_id: str, uc_data: dict):
    # get master
    master = get_master_by_id(db, master_id)
    
    # create UC with auto-fetched VIN
    uc_dict = {
        'master_record_id': master_id,
        'vehicle_id_number': master.vehicle_id_number,  # auto-fetch VIN
    }
    
    # add user-provided fields(user can override auto-fetched values)
    for field, value in uc_data.items():
        if value is not None:  # only if user provided a value
            uc_dict[field] = value
        else:
            if hasattr(master, field):
                uc_dict[field] = getattr(master, field)
    
    # create UC object
    uc = VehicleRegistrationUnderCover(**uc_dict)
    db.add(uc)
    db.commit()
    db.refresh(uc)
    return uc

# create fc

def create_fictitious(db: Session, master_id: str, fc_data: dict):
    """
    Create FC record:
    1. Validate master exists
    2. Auto-fetch master's VIN
    3. Use provided values, fallback to master values if None
    """
    # get master
    master = get_master_by_id(db, master_id)
    
    # create FC with auto-fetched VIN
    fc_dict = {
        'master_record_id': master_id,
        'vehicle_id_number': master.vehicle_id_number,  # auto-fetch VIN
    }
    
    # add user-provided fields(user can override auto-fetched values)
    for field, value in fc_data.items():
        if value is not None:  # only if user provided a value
            fc_dict[field] = value
        else:  # if user didnt provide, use masters value
            if hasattr(master, field):
                fc_dict[field] = getattr(master, field)
    
    # create FC object
    fc = VehicleRegistrationFictitious(**fc_dict)
    db.add(fc)
    db.commit()
    db.refresh(fc)
    return fc

# get uc/fc for a master record

def get_undercover_by_master(db: Session, master_id: str):
    """Get all UC records for a specific Master"""
    get_master_by_id(db, master_id)  # Verify master exists
    return db.query(VehicleRegistrationUnderCover).filter(
        VehicleRegistrationUnderCover.master_record_id == master_id
    ).all()

# get all FC records for a specific master
def get_fictitious_by_master(db: Session, master_id: str):
    get_master_by_id(db, master_id)  # verify master exists
    return db.query(VehicleRegistrationFictitious).filter(
        VehicleRegistrationFictitious.master_record_id == master_id
    ).all()

#mark uc or fc as active/inactive

def mark_undercover_active(db: Session, uc_id: int):
    """Mark UC as active"""
    uc = db.query(VehicleRegistrationUnderCover).get(uc_id)
    if not uc:
        raise HTTPException(status_code=404, detail="UC record not found")
    uc.active_status = True
    db.commit()
    return uc

def mark_undercover_inactive(db: Session, uc_id: int):
    """Mark UC as inactive"""
    uc = db.query(VehicleRegistrationUnderCover).get(uc_id)
    if not uc:
        raise HTTPException(status_code=404, detail="UC record not found")
    uc.active_status = False
    db.commit()
    return uc

def mark_fictitious_active(db: Session, fc_id: int):
    fc = db.query(VehicleRegistrationFictitious).get(fc_id)
    if not fc:
        raise HTTPException(status_code=404, detail="FC record not found")
    fc.active_status = True
    db.commit()
    return fc

def mark_fictitious_inactive(db: Session, fc_id: int):
    fc = db.query(VehicleRegistrationFictitious).get(fc_id)
    if not fc:
        raise HTTPException(status_code=404, detail="FC record not found")
    fc.active_status = False
    db.commit()
    return fc
