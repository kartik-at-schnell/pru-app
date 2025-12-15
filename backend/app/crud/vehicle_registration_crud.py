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
    VehicleRegistrationContactCreateBody,
    VehicleRegistrationFictitiousTrapInfoCreateBody,
    VehicleRegistrationMasterCreate,
    VehicleRegistrationMasterBase,
    VehicleRegistrationReciprocalIssuedCreateBody,
    VehicleRegistrationReciprocalReceivedCreateBody,
    VehicleRegistrationUnderCoverTrapInfoCreateBody
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
        active_status=payload.active_status,
        expiration_date=payload.expiration_date,
        date_issued = payload.date_issued,
        date_received = payload.date_received,
        date_fee_received = payload.date_fee_received,
        amount_paid = payload.amount_paid,
        amount_due = payload.amount_due,
        amount_received = payload.amount_received,
        use_tax = payload.use_tax,
        sticker_issued = payload.sticker_issued,
        sticker_numbers = payload.sticker_numbers,
        cert_type = payload.cert_type,            
        mp =payload.mp,               
        mo =payload.mo,                    
        axl =payload.axl,                  
        wc =payload.wc,                    
        cc_alco = payload.cc_alco,
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
        active_status=payload.active_status,
        officer=payload.officer
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
        active_status=payload.active_status,
        officer=payload.officer
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

    query = query.filter(model.is_suppressed == False) # exclude suppressed records

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
            # joinedload(VehicleRegistrationMaster.reciprocal_issued),  # these two are removed for now since relations has been removed temporarily
            # joinedload(VehicleRegistrationMaster.reciprocal_received),
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


def create_contact(db: Session, master_id: int, payload: VehicleRegistrationContactCreateBody):

    master = get_master_by_id(db, master_id)
    
    contact = VehicleRegistrationContact(
        master_record_id=master_id,
        contact_name=payload.contact_name,
        department=payload.department,
        email=payload.email,
        phone_number=payload.phone_number,
        address=payload.address,
        alt_contact_1=payload.alt_contact_1,
        alt_contact_2=payload.alt_contact_2,
        alt_contact_3=payload.alt_contact_3,
        alt_contact_4=payload.alt_contact_4
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact


def get_contact(db: Session, contact_id: int):

    contact = db.query(VehicleRegistrationContact).filter(
        VehicleRegistrationContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact


def get_contacts_by_master(db: Session, master_id: int):

    get_master_by_id(db, master_id)
    
    contacts = db.query(VehicleRegistrationContact).filter(
        VehicleRegistrationContact.master_record_id == master_id
    ).all()
    
    return contacts


def update_contact(db: Session, contact_id: int, payload: VehicleRegistrationContactCreateBody):    
  
    contact = get_contact(db, contact_id)
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)

    return contact


def get_all_contacts(db: Session, skip: int = 0, limit: int = 100):

    contacts = db.query(VehicleRegistrationContact).offset(skip).limit(limit).all()
    return contacts

# create reciprocal issued
def create_reciprocal_issued(db: Session, payload: VehicleRegistrationReciprocalIssuedCreateBody):

    master = None
    if payload.master_record_id is not None:
        master = get_master_by_id(db, payload.master_record_id)
        if not master:
            raise HTTPException(status_code=404, detail=f"Master record {payload.master_record_id} not found")
    
    reciprocal = VehicleRegistrationReciprocalIssued(
        master_record_id=payload.master_record_id,
        description=payload.description,
        license_plate=payload.license_number,
        issuing_state=payload.issuing_state,
        recipient_state=payload.recipient_state,
        year_of_renewal=payload.year_of_renewal,
        cancellation_date=payload.cancellation_date,
        sticker_number=payload.sticker_number,
        issuing_authority=payload.issuing_authority,
        agreement_issued_id=payload.agreement_issued_id
    )
    
    db.add(reciprocal)
    db.commit()
    db.refresh(reciprocal)
    return reciprocal


def get_reciprocal_issued(db: Session, master_id: Optional[int] = None, skip: int = 0, limit: int = 50):
    query = db.query(VehicleRegistrationReciprocalIssued)
    if master_id is not None:
        query = query.filter(VehicleRegistrationReciprocalIssued.master_record_id == master_id)
    return query.offset(skip).limit(limit).all()


def get_reciprocal_issued_by_master(db: Session, master_id: int):
    get_master_by_id(db, master_id)
    
    reciprocals = db.query(VehicleRegistrationReciprocalIssued).filter(
        VehicleRegistrationReciprocalIssued.master_record_id == master_id
    ).all()
    return reciprocals

def get_reciprocal_issued_by_id(db: Session, reciprocal_id: int):
    reciprocal = db.query(VehicleRegistrationReciprocalIssued).filter(
        VehicleRegistrationReciprocalIssued.id == reciprocal_id
    ).first()
    
    if not reciprocal:
        raise HTTPException(status_code=404, detail="Reciprocal Issued record not found")
    
    return reciprocal


def update_reciprocal_issued(db: Session, reciprocal_id: int, payload: VehicleRegistrationReciprocalIssuedCreateBody):
    reciprocal = get_reciprocal_issued(db, reciprocal_id)
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(reciprocal, key):
            setattr(reciprocal, key, value)
    
    db.commit()
    db.refresh(reciprocal)
    return reciprocal


def delete_reciprocal_issued(db: Session, reciprocal_id: int):
    reciprocal = get_reciprocal_issued(db, reciprocal_id)
    db.delete(reciprocal)
    db.commit()
    return {"message": f"Reciprocal Issued {reciprocal_id} deleted successfully"}


def get_all_reciprocal_issued(db: Session, skip: int = 0, limit: int = 100):
    reciprocals = db.query(VehicleRegistrationReciprocalIssued).offset(skip).limit(limit).all()
    return reciprocals


# reciprocal received
def create_reciprocal_received(db: Session, payload: VehicleRegistrationReciprocalReceivedCreateBody):
    master = None
    if payload.master_record_id is not None:
        master = get_master_by_id(db, payload.master_record_id)
        if not master:
            raise HTTPException(status_code=404, detail=f"Master record {payload.master_record_id} not found")
    
    reciprocal = VehicleRegistrationReciprocalReceived(
        master_record_id=payload.master_record_id,
        description=payload.description,
        license_plate=payload.license_number,
        issuing_state=payload.issuing_state,
        recipient_state=payload.recipient_state,
        year_of_renewal=payload.year_of_renewal,
        cancellation_date=payload.cancellation_date,
        recieved_date=payload.recieved_date,
        sticker_number=payload.sticker_number,
        issuing_authority=payload.issuing_authority
    )
    
    db.add(reciprocal)
    db.commit()
    db.refresh(reciprocal)
    return reciprocal


def get_reciprocal_received(db: Session, reciprocal_id: int):
    reciprocal = db.query(VehicleRegistrationReciprocalReceived).filter(
        VehicleRegistrationReciprocalReceived.id == reciprocal_id
    ).first()
    
    if not reciprocal:
        raise HTTPException(status_code=404, detail="Reciprocal Received record not found")
    return reciprocal


def get_reciprocal_received_by_master(db: Session, master_id: int):
    get_master_by_id(db, master_id)
    
    reciprocals = db.query(VehicleRegistrationReciprocalReceived).filter(
        VehicleRegistrationReciprocalReceived.master_record_id == master_id
    ).all()
    return reciprocals


def update_reciprocal_received(db: Session, reciprocal_id: int, payload: VehicleRegistrationReciprocalReceivedCreateBody):
    reciprocal = get_reciprocal_received(db, reciprocal_id)
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(reciprocal, key):
            setattr(reciprocal, key, value)
    
    db.commit()
    db.refresh(reciprocal)
    return reciprocal


def delete_reciprocal_received(db: Session, reciprocal_id: int):
    reciprocal = get_reciprocal_received(db, reciprocal_id)
    db.delete(reciprocal)
    db.commit()
    return {"message": f"Reciprocal Received {reciprocal_id} deleted successfully"}


def get_all_reciprocal_received(db: Session, skip: int = 0, limit: int = 100):
    reciprocals = db.query(VehicleRegistrationReciprocalReceived).offset(skip).limit(limit).all()
    return reciprocals


# trap info undercover
def create_trap_info_undercover(db: Session, undercover_id: int, payload: VehicleRegistrationUnderCoverTrapInfoCreateBody):
    uc = db.query(VehicleRegistrationUnderCover).filter(
        VehicleRegistrationUnderCover.id == undercover_id
    ).first()
    
    if not uc:
        raise HTTPException(status_code=404, detail="Undercover record not found")
    
    trap_info = VehicleRegistrationUnderCoverTrapInfo(
        undercover_id=undercover_id,
        request_date=payload.request_date,
        number=payload.number,
        officer=payload.officer,
        location=payload.location,
        reason=payload.reason,
        # verified_by=payload.verified_by,
        # verification_date=payload.verification_date
    )
    
    db.add(trap_info)
    db.commit()
    db.refresh(trap_info)
    return trap_info


def get_trap_info_undercover(db: Session, trap_info_id: int):
    trap_info = db.query(VehicleRegistrationUnderCoverTrapInfo).filter(
        VehicleRegistrationUnderCoverTrapInfo.id == trap_info_id
    ).first()
    
    if not trap_info:
        raise HTTPException(status_code=404, detail="Trap Info (UC) not found")
    return trap_info


def get_trap_info_undercover_by_uc(db: Session, undercover_id: int):
    uc = db.query(VehicleRegistrationUnderCover).filter(
        VehicleRegistrationUnderCover.id == undercover_id
    ).first()
    
    if not uc:
        raise HTTPException(status_code=404, detail="Undercover record not found")
    
    trap_infos = db.query(VehicleRegistrationUnderCoverTrapInfo).filter(
        VehicleRegistrationUnderCoverTrapInfo.undercover_id == undercover_id
    ).all()
    return trap_infos


def update_trap_info_undercover(db: Session, trap_info_id: int, payload: VehicleRegistrationUnderCoverTrapInfoCreateBody):
    trap_info = get_trap_info_undercover(db, trap_info_id)
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(trap_info, key):
            setattr(trap_info, key, value)
    
    db.commit()
    db.refresh(trap_info)
    return trap_info


def delete_trap_info_undercover(db: Session, trap_info_id: int):
    trap_info = get_trap_info_undercover(db, trap_info_id)
    db.delete(trap_info)
    db.commit()
    return {"message": f"Trap Info (UC) {trap_info_id} deleted successfully"}


def get_all_trap_info_undercover(db: Session, skip: int = 0, limit: int = 100):
    trap_infos = db.query(VehicleRegistrationUnderCoverTrapInfo).offset(skip).limit(limit).all()
    return trap_infos


# trap info fictitious
def create_trap_info_fictitious(db: Session, fictitious_id: int, payload: VehicleRegistrationFictitiousTrapInfoCreateBody):
    fc = db.query(VehicleRegistrationFictitious).filter(
        VehicleRegistrationFictitious.id == fictitious_id
    ).first()
    
    if not fc:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
    
    trap_info = VehicleRegistrationFictitiousTrapInfo(
        fictitious_id=fictitious_id,
        request_date=payload.request_date,
        number=payload.number,
        officer=payload.officer,
        location=payload.location,
        reason=payload.reason
    )
    
    db.add(trap_info)
    db.commit()
    db.refresh(trap_info)
    return trap_info


def get_trap_info_fictitious(db: Session, trap_info_id: int):
    trap_info = db.query(VehicleRegistrationFictitiousTrapInfo).filter(
        VehicleRegistrationFictitiousTrapInfo.id == trap_info_id
    ).first()
    
    if not trap_info:
        raise HTTPException(status_code=404, detail="Trap Info (FC) not found")
    return trap_info


def get_trap_info_fictitious_by_fc(db: Session, fictitious_id: int):
    fc = db.query(VehicleRegistrationFictitious).filter(
        VehicleRegistrationFictitious.id == fictitious_id
    ).first()
    
    if not fc:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
    
    trap_infos = db.query(VehicleRegistrationFictitiousTrapInfo).filter(
        VehicleRegistrationFictitiousTrapInfo.fictitious_id == fictitious_id
    ).all()
    return trap_infos


def update_trap_info_fictitious(db: Session, trap_info_id: int, payload: VehicleRegistrationFictitiousTrapInfoCreateBody):
    trap_info = get_trap_info_fictitious(db, trap_info_id)
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(trap_info, key):
            setattr(trap_info, key, value)
    
    db.commit()
    db.refresh(trap_info)
    return trap_info


def delete_trap_info_fictitious(db: Session, trap_info_id: int):
    trap_info = get_trap_info_fictitious(db, trap_info_id)
    db.delete(trap_info)
    db.commit()
    return {"message": f"Trap Info (FC) {trap_info_id} deleted successfully"}


def get_all_trap_info_fictitious(db: Session, skip: int = 0, limit: int = 100):
    trap_infos = db.query(VehicleRegistrationFictitiousTrapInfo).offset(skip).limit(limit).all()
    return trap_infos