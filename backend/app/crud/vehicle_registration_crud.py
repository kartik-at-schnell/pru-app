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
    VehicleRegistrationMasterBase,
    VehicleRegistrationCreateRequest
)

def create_vehicle_record(db: Session, record_data: VehicleRegistrationCreateRequest):

    record_type = record_data.record_type.lower() if record_data.record_type else "master"
    
    # Extract common fields
    data_dict = {
        "id": record_data.id,
        "license_number": record_data.license_number,
        "vehicle_id_number": record_data.vehicle_id_number,
        "registered_owner": record_data.registered_owner,
        "make": record_data.make,
        "model": record_data.model,
        "year_model": record_data.year_model,
        "approval_status": record_data.approval_status,
    }
    
    try:
        if record_type == "undercover":
            new_record = VehicleRegistrationUnderCover(**data_dict)
        elif record_type == "fictitious":
            new_record = VehicleRegistrationFictitious(**data_dict)
        else:  # default to master
            new_record = VehicleRegistrationMaster(**data_dict)
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create {record_type} record: {str(e)}")


# get by id - search across all 3 tables
def get_vehicle_by_id(db: Session, record_id: str):
    
    # Try Master first
    record = db.query(VehicleRegistrationMaster).filter(
        VehicleRegistrationMaster.id == record_id
    ).first()
    if record:
        return record
    
    # Try Undercover
    record = db.query(VehicleRegistrationUnderCover).filter(
        VehicleRegistrationUnderCover.id == record_id
    ).first()
    if record:
        return record
    
    # Try Fictitious
    record = db.query(VehicleRegistrationFictitious).filter(
        VehicleRegistrationFictitious.id == record_id
    ).first()
    if record:
        return record
    
    return None

# get all, this is for search bar - with optional table filtering
def get_all_vehicles(
    db: Session, 
    skip: int = 0, 
    limit: int = 30,
    record_type: Optional[str] = None,
    search: Optional[str] = None
):
    
    records = []
    
    # Build queries based on record_type filter
    if record_type is None or record_type == "master":
        query = db.query(VehicleRegistrationMaster)
        if search:
            query = query.filter(
                (VehicleRegistrationMaster.license_number.ilike(f"%{search}%")) |
                (VehicleRegistrationMaster.vehicle_id_number.ilike(f"%{search}%"))
            )
        records.extend(query.offset(skip).limit(limit).all())
    
    if record_type is None or record_type == "undercover":
        query = db.query(VehicleRegistrationUnderCover)
        if search:
            query = query.filter(
                (VehicleRegistrationUnderCover.license_number.ilike(f"%{search}%")) |
                (VehicleRegistrationUnderCover.vehicle_id_number.ilike(f"%{search}%"))
            )
        records.extend(query.offset(skip).limit(limit).all())
    
    if record_type is None or record_type == "fictitious":
        query = db.query(VehicleRegistrationFictitious)
        if search:
            query = query.filter(
                (VehicleRegistrationFictitious.license_number.ilike(f"%{search}%")) |
                (VehicleRegistrationFictitious.vehicle_id_number.ilike(f"%{search}%"))
            )
        records.extend(query.offset(skip).limit(limit).all())
    
    return records

# update - searches across all tables
def update_vehicle_record(db: Session, record_id: str, update_data: VehicleRegistrationMasterBase):
    """
    Update vehicle record (searches all tables)
    Returns: updated record or None
    """
    
    record = get_vehicle_by_id(db, record_id)
    if not record:
        return None
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# delete - searches across all tables
def delete_vehicle_record(db: Session, record_id: str):
    """
    Delete vehicle record (searches all tables)
    Returns: deleted record or None
    """
    
    record = get_vehicle_by_id(db, record_id)
    if not record:
        return None
    
    db.delete(record)
    db.commit()
    return record

# function to get all the details for one vehicle
def get_vehicle_master_details(db: Session, master_id: str):
    """
    Get complete vehicle record with all related data (Master table only)
    Includes: contacts, reciprocal issued/received, undercover records, fictitious records
    """
    
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
