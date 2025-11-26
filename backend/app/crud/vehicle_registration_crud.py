from app.models import VehicleRegistrationReciprocalIssued, VehicleRegistrationMaster
from app.schemas.vehicle_registration_schema import (
    VRReciprocalReceivedCreate,
    VRReciprocalReceivedUpdate,
    VehicleRegistrationReciprocalIssuedCreateBody,
    VehicleRegistrationReciprocalIssuedUpdate,
    VehicleRegistrationReciprocalReceivedCreateBody 
)
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
    FictitiousCreateRequest,
    MasterCreateRequest,
    UnderCoverCreateRequest,
    VehicleRegistrationMasterCreate,
    VehicleRegistrationMasterBase
)
from ..models.base import BaseModel

#Create records

def create_master_record(db, payload: MasterCreateRequest):
    master = VehicleRegistrationMaster(
        license_number=payload.license_number,
        vehicle_id_number=payload.vehicle_id_number,
        registered_owner=payload.registered_owner,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
        make=payload.make,
        model=payload.model,
        year_model=payload.year_model,
        body_type=payload.body_type,
        type_license=payload.type_license,
        type_vehicle=payload.type_vehicle,
        active_status=payload.active_status
    )
    db.add(master)
    db.commit()
    db.refresh(master)
    return master

def create_undercover_record(db, payload: UnderCoverCreateRequest):
    master = db.query(VehicleRegistrationMaster).filter_by(id=payload.master_record_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master record not found")

    # VIN logic
    vin = payload.vehicle_id_number or master.vehicle_id_number
    if payload.vehicle_id_number and payload.vehicle_id_number != master.vehicle_id_number:
        raise HTTPException(status_code=400, detail="Provided VIN does not match master record")

    record = VehicleRegistrationUnderCover(
        master_record_id=master.id,
        vehicle_id_number=vin,
        license_number=payload.license_number,
        registered_owner=payload.registered_owner,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
        make=payload.make,
        year_model=payload.year_model,
        class_type=payload.class_type,
        type_license=payload.type_license,
        expiration_date=payload.expiration_date,
        date_issued=payload.date_issued,
        date_fee_received=payload.date_fee_received,
        amount_paid=payload.amount_paid,
        active_status=payload.active_status
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def create_fictitious_record(db, payload: FictitiousCreateRequest):
    master = db.query(VehicleRegistrationMaster).filter_by(id=payload.master_record_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master record not found")

    vin = payload.vehicle_id_number or master.vehicle_id_number
    if payload.vehicle_id_number and payload.vehicle_id_number != master.vehicle_id_number:
        raise HTTPException(status_code=400, detail="Provided VIN does not match master record")

    record = VehicleRegistrationFictitious(
        master_record_id=master.id,
        vehicle_id_number=vin,
        license_number=payload.license_number,
        registered_owner=payload.registered_owner,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
        make=payload.make,
        model=payload.model,
        year_model=payload.year_model,
        vlp_class=payload.vlp_class,
        amount_due=payload.amount_due,
        amount_received=payload.amount_received,
        active_status=payload.active_status
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

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
def update_vehicle_record(db: Session, record_id: int, update_data: BaseModel, record_type: str = "master"):

    if record_type == "undercover":
        model = VehicleRegistrationUnderCover
    elif record_type == "fictitious":
        model = VehicleRegistrationFictitious
    else:
        model = VehicleRegistrationMaster

    record = db.query(model).filter(model.id == record_id).first()
    if not record:
        return None

    for key, value in update_data.model_dump(exclude_unset=True).items():
        if hasattr(record, key):
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

# mark record inactive
def mark_inactive(db, record_id: int):
    record = db.query(VehicleRegistrationMaster).get(record_id)
    if(record):
        record.active_status = False

        # cascade to children in fictitious and undercoveer records
        db.query(VehicleRegistrationUnderCover).filter(
            VehicleRegistrationUnderCover.master_record_id == record_id
        ).update({"active_status": False}, synchronize_session=False)
        
        db.query(VehicleRegistrationFictitious).filter(
            VehicleRegistrationFictitious.master_record_id == record_id
        ).update({"active_status": False}, synchronize_session=False)

        db.commit()
        return record
    
    return None

#mark active
def mark_active(db, record_id: int):
    record = get_vehicle_by_id(db, record_id)

    if(record):
        record.active_status = True

        # cascade to children
        db.query(VehicleRegistrationUnderCover).filter(
            VehicleRegistrationUnderCover.master_record_id == record_id
        ).update({"active_status": True}, synchronize_session=False)
        
        db.query(VehicleRegistrationFictitious).filter(
            VehicleRegistrationFictitious.master_record_id == record_id
        ).update({"active_status": True}, synchronize_session=False)

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

# ================================
# RECIPROCAL ISSUED CRUD (UPDATED)
# ================================

def create_reciprocal_issued_record(
    db: Session, 
    payload: VehicleRegistrationReciprocalIssuedCreateBody
):
    record = VehicleRegistrationReciprocalIssued(
        master_record_id = payload.master_record_id,
        description = payload.description,
        license_plate = payload.license_plate,
        state = payload.state,
        year_of_renewal = payload.year_of_renewal,
        cancellation_date = payload.cancellation_date,
        sticker_number = payload.sticker_number,
        created_by = payload.created_by
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Insert failed: {str(e)}")

    return record


def get_reciprocal_record_by_id(db: Session, record_id: int):
    record = db.query(VehicleRegistrationReciprocalIssued).filter_by(id=record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


def get_all_reciprocal_records(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(VehicleRegistrationReciprocalIssued)
        .order_by(VehicleRegistrationReciprocalIssued.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_reciprocal_record(
    db: Session, 
    record_id: int, 
    payload: VehicleRegistrationReciprocalIssuedUpdate
):
    record = db.query(VehicleRegistrationReciprocalIssued).filter_by(id=record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if hasattr(record, key):
            setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    return record


def delete_reciprocal_record(db: Session, record_id: int):
    record = db.query(VehicleRegistrationReciprocalIssued).filter_by(id=record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    try:
        db.delete(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    return {"message": "Deleted successfully"}

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
    ).all()

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

# bulk ops

# bulk approve
def bulk_approve(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id.in_(record_ids),
            VehicleRegistrationMaster.approval_status != "approved"
        ).update(
            {"approval_status": "approved"},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk approve failed: {str(e)}")

# bulk reject
def bulk_reject(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id.in_(record_ids),
            VehicleRegistrationMaster.approval_status != "rejected"
        ).update(
            {"approval_status": "rejected"},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk reject failed: {str(e)}")

# bulk onhold
def bulk_set_on_hold(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id.in_(record_ids),
            VehicleRegistrationMaster.approval_status != "on_hold"
        ).update(
            {"approval_status": "on_hold"},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk on-hold failed: {str(e)}")

#flag rcords active in bulk 
def bulk_active(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id.in_(record_ids),
            VehicleRegistrationMaster.active_status == False
        ).update(
            {"active_status": True},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk activate failed: {str(e)}")

#flag multiple records inactive
def bulk_inactive(db: Session, record_ids: List[int]):
    try:
        updated_count = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id.in_(record_ids),
            VehicleRegistrationMaster.active_status == True
        ).update(
            {"active_status": False},
            synchronize_session=False
        )
        db.commit()
        return updated_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk deactivate failed: {str(e)}")

# bulk delete 
def bulk_delete(db: Session, record_ids: List[int]):
    try:
        deleted_count = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id.in_(record_ids)
        ).delete(synchronize_session=False)
        db.commit()
        return deleted_count
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")

def create_vr_reciprocal_received(db: Session, payload: VRReciprocalReceivedCreate):
    record = VehicleRegistrationReciprocalReceived(
        registered_owner = payload.registered_owner,
        owner_address = payload.owner_address,
        description = payload.description,
        license_plate = payload.license_plate,
        sticker_number = payload.sticker_number,
        year_of_renewal = payload.year_of_renewal,
        cancellation_date = payload.cancellation_date,
        recieved_date = payload.recieved_date,
        expiry_date = payload.expiry_date,
        issuing_authority = payload.issuing_authority,
        issuing_state = payload.issuing_state,
        recipent_state = payload.recipent_state,
        created_by = payload.created_by
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_vr_reciprocal_received(db: Session):
    return db.query(VehicleRegistrationReciprocalReceived).all()

def update_vr_reciprocal_received(db: Session, record_id: int, payload: VRReciprocalReceivedUpdate):
    record = db.query(VehicleRegistrationReciprocalReceived).filter_by(id=record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    payload_dict = payload.model_dump(exclude_unset=True)

    for field, value in payload_dict.items():
        setattr(record, field, value)

    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def delete_vr_reciprocal_received(db: Session, record_id: int):
    record = db.query(VehicleRegistrationReciprocalReceived).filter(
        VehicleRegistrationReciprocalReceived.id == record_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()
    return True

