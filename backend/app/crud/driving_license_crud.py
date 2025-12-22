from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.driving_license import (
    DriverLicenseOriginalRecord,
    DriverLicenseContact,
    DriverLicenseFictitiousTrap,
    DriverLicenseFictitious
)
from app.schemas.driving_license_schema import (
    DriverLicenseOriginalCreate,
    DriverLicenseOriginalUpdate,
    DriverLicenseContactCreate,
    DriverLicenseFictitiousTrapCreate,
    DriverLicenseSearchQuery,
    DriverLicenseFictitiousCreate,
    DriverLicenseFictitiousUpdate
)
from app.models.base import ActionType
from app.models import driving_license


# Create ops

# create main record
def create_original_record(db: Session, payload: DriverLicenseOriginalCreate):
    
    # generate record_id (DL001, DL002 etc)
    count = db.query(DriverLicenseOriginalRecord).count()
    next_id = count + 1
    record_id = f"DL{str(next_id).zfill(3)}"

    original = DriverLicenseOriginalRecord(
        record_id=record_id,
        tln=payload.tln,
        tfn=payload.tfn,
        tdl=payload.tdl,
        fln=payload.fln,
        ffn=payload.ffn,
        fdl=payload.fdl,
        agency=payload.agency,
        contact=payload.contact,
        date_issued=payload.date_issued,
        modified=payload.modified,

        approval_status="pending",  # default approval status
        active_status=True  # default active status
    )
    
    db.add(original)
    db.commit()
    db.refresh(original)
    
    return original

# create contact
def create_contact(db: Session, original_record_id: int, payload: DriverLicenseContactCreate):
    
    #verify original record exists
    original = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == original_record_id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Original record not found")
    
    contact = DriverLicenseContact(
        original_record_id=original_record_id,
        contact_name=payload.contact_name,
        department1=payload.department1,
        address=payload.address,
        email=payload.email,
        phone_number=payload.phone_number,
        alternative_contact1=payload.alternative_contact1,
        alternative_contact2=payload.alternative_contact2,
        alternative_contact3=payload.alternative_contact3,
        alternative_contact4=payload.alternative_contact4,
        master_record_id=payload.master_record_id,
        is_active=payload.is_active
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact

# new fict trap record
def create_fictitious_trap(db: Session, fictitious_record_id: int, payload: DriverLicenseFictitiousTrapCreate):

    #verify fictitious record exists
    fictitious_record = db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.id == fictitious_record_id
    ).first()
    
    if not fictitious_record:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
    
    trap = DriverLicenseFictitiousTrap(
        fictitious_record_id=fictitious_record_id,
        # mandatory fields
        # date=payload.date,
        number=payload.number,
        fictitious_id=payload.fictitious_id,
        # 0ptional fields
        test=payload.test,
        title=payload.title,
        compliance_asset_id=payload.compliance_asset_id,
        color_tag=payload.color_tag,
        test2=payload.test2,
        content_type=payload.content_type,
        attachments=payload.attachments,
        type=payload.type,
        item_child_count=payload.item_child_count,
        folder_child_count=payload.folder_child_count,
        label_setting=payload.label_setting,
        retention_label=payload.retention_label,
        retention_label_applied=payload.retention_label_applied,
        label_applied_by=payload.label_applied_by,
        item_is_record=payload.item_is_record,
        app_created_by=payload.app_created_by,
        app_modified_by=payload.app_modified_by,
        version=payload.version
    )
    
    db.add(trap)
    db.commit()
    db.refresh(trap)
    
    return trap

# search

def search_driving_license(db: Session, query: DriverLicenseSearchQuery):
    q = db.query(driving_license)
    if query.record_id:
        q = q.filter(driving_license.id == query.record_id)
    if query.tdl_number:
        q = q.filter(driving_license.tdl_number.ilike(f"%{query.tdl_number}%"))
    if query.fdl_number:
        q = q.filter(driving_license.fdl_number.ilike(f"%{query.fdl_number}%"))
    return q.all()

# Read OPs

# get all
def get_all_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_status: Optional[str] = None,
    approval_status: Optional[str] = None,
    active_only: Optional[bool] = True
):
    query = db.query(DriverLicenseOriginalRecord)
    
    # filters
    if active_only:
        query = query.filter(DriverLicenseOriginalRecord.active_status == True)
    
    if active_status:
        query = query.filter(DriverLicenseOriginalRecord.active_status == active_status)
    
    if approval_status:
        query = query.filter(DriverLicenseOriginalRecord.approval_status == approval_status)
    
    # order by most recent
    query = query.order_by(DriverLicenseOriginalRecord.created_at.desc())

    query = query.filter(DriverLicenseOriginalRecord.is_suppressed == False)
    
    records = query.offset(skip).limit(limit).all()
    
    return records

# options dropdown
def get_record_options(db: Session):
    return db.query(DriverLicenseOriginalRecord.id, DriverLicenseOriginalRecord.record_id, DriverLicenseOriginalRecord.tln).filter(
        DriverLicenseOriginalRecord.active_status == True
    ).all()

# single record with all related record 
def get_record_by_id(db: Session, record_id: int):

    record = db.query(DriverLicenseOriginalRecord).options(
        joinedload(DriverLicenseOriginalRecord.contacts),
        joinedload(DriverLicenseOriginalRecord.fictitious_records).joinedload(DriverLicenseFictitious.traps)
    ).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return record

# get by tln
def get_record_by_tln(db: Session, tln: str):
    
    record = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.tln == tln
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return record


def get_record_by_tdl(db: Session, tdl: str):
    
    record = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.tdl == tdl
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return record

# Update ops

# update main record - dl 
def update_original_record(db: Session, record_id: int, payload: DriverLicenseOriginalUpdate):
    
    record = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return record


# DELETE OPERATIONS

#
def soft_delete_record(db: Session, record_id: int):
    
    record = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record.active_status = False
    db.commit()
    db.refresh(record)
    
    return {"message": f"Record {record_id} soft deleted successfully"}

# remove from db
def hard_delete_record(db: Session, record_id: int):
    
    record = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Delete related contacts
    db.query(DriverLicenseContact).filter(
        DriverLicenseContact.original_record_id == record_id
    ).delete()
    
    # Delete related fictitious traps
    # Since we moved traps to fictitious records and don't have DB-level cascade:
    # 1. Get IDs of fictitious records
    fictitious_records = db.query(DriverLicenseFictitious.id).filter(
        DriverLicenseFictitious.original_record_id == record_id
    ).all()
    fictitious_ids = [r.id for r in fictitious_records]
    
    if fictitious_ids:
        db.query(DriverLicenseFictitiousTrap).filter(
            DriverLicenseFictitiousTrap.fictitious_record_id.in_(fictitious_ids)
        ).delete(synchronize_session=False)

    # 2. Delete fictitious records
    db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.original_record_id == record_id
    ).delete(synchronize_session=False)
    
    # Delete the original record
    db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {"message": f"Record {record_id} permanently deleted"}

# undo soft delete
def restore_record(db: Session, record_id: int):
    
    record = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record.active_status = True
    db.commit()
    db.refresh(record)
    
    return record


# CONTACT

#get all (across all recs)
def get_all_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    contacts = db.query(DriverLicenseContact).filter(
        DriverLicenseContact.is_active == True
    ).order_by(
        DriverLicenseContact.created.desc()
    ).offset(skip).limit(limit).all()
    return contacts

# detailed contact 
def get_contact_by_id(db: Session, contact_id: int):
    contact = db.query(DriverLicenseContact).filter(
        DriverLicenseContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
# get all for one record
def get_contacts_by_record(db: Session, record_id: int):
    
    return db.query(DriverLicenseContact).filter(
        DriverLicenseContact.original_record_id == record_id,
        DriverLicenseContact.is_active == True
    ).all()


# get single contact
def get_contact_by_id(db: Session, contact_id: int):
    contact = db.query(DriverLicenseContact).filter(
        DriverLicenseContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    return contact


# update
def update_contact(db: Session, contact_id: int, payload: DriverLicenseContactCreate):
    
    contact = db.query(DriverLicenseContact).filter(
        DriverLicenseContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    
    return contact

# remove contact
def delete_contact(db: Session, contact_id: int):
    
    contact = db.query(DriverLicenseContact).filter(
        DriverLicenseContact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    
    return {"message": f"Contact {contact_id} deleted successfully"}


# FICTITIOUS TRAP

# get all
def get_all_traps(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    traps = db.query(DriverLicenseFictitiousTrap).order_by(
        DriverLicenseFictitiousTrap.created_at.desc()
    ).offset(skip).limit(limit).all()
    return traps

# single detailed record
def get_trap_by_id(db: Session, trap_id: int):
    trap = db.query(DriverLicenseFictitiousTrap).filter(
        DriverLicenseFictitiousTrap.id == trap_id
    ).first()
    
    if not trap:
        raise HTTPException(status_code=404, detail="Fictitious trap not found")
    
    return trap

# get all for one fictitious record
def get_traps_by_fictitious_record(db: Session, fictitious_record_id: int):
    
    traps = db.query(DriverLicenseFictitiousTrap).filter(
        DriverLicenseFictitiousTrap.fictitious_record_id == fictitious_record_id
    ).all()
    
    return traps

#update 
def update_trap(db: Session, trap_id: int, payload: DriverLicenseFictitiousTrapCreate):
    trap = db.query(DriverLicenseFictitiousTrap).filter(
        DriverLicenseFictitiousTrap.id == trap_id
    ).first()
    
    if not trap:
        raise HTTPException(status_code=404, detail="Fictitious trap not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trap, field, value)
    
    db.commit()
    db.refresh(trap)
    return trap

# delete
def delete_trap(db: Session, trap_id: int):
    
    trap = db.query(DriverLicenseFictitiousTrap).filter(
        DriverLicenseFictitiousTrap.id == trap_id
    ).first()
    
    if not trap:
        raise HTTPException(status_code=404, detail="Fictitious trap not found")
    
    db.delete(trap)
    db.commit()
    
    return {"message": f"Fictitious trap {trap_id} deleted successfully"}


# STATS

# get count of records by status, for dashboard
def get_records_count(db: Session):
    total = db.query(DriverLicenseOriginalRecord).count()
    active = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.active_status == True
    ).count()
    
    approved = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.approval_status == "approved"
    ).count()
    pending = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.approval_status == "pending"
    ).count()
    rejected = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.approval_status == "rejected"
    ).count()
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    }


# FICTITIOUS RECORD

# create
# create
def create_fictitious_record(db: Session, original_record_id: int, payload: DriverLicenseFictitiousCreate, user_id: Optional[int] = None):
    
    #verify original record exists
    original = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == original_record_id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Original record not found")
        
    fictitious = DriverLicenseFictitious(
        original_record_id=original_record_id,
        fake_first_name=payload.fake_first_name,
        fake_last_name=payload.fake_last_name,
        fake_license_number=payload.fake_license_number,
        agency=payload.agency,
        contact_details=payload.contact_details,
        date_issued=payload.date_issued,
        approval_status=payload.approval_status,
        is_active=payload.is_active,
        created_by=user_id,
        updated_by=user_id
    )
    
    db.add(fictitious)
    db.commit()
    db.refresh(fictitious)
    
    return fictitious


# Archive / Deactivate functions

def archive_driver_license(db: Session, record_id: int):
    record = get_record_by_id(db, record_id)
    record.active_status = False
    db.commit()
    db.refresh(record)
    return record


def deactivate_contact(db: Session, contact_id: int):
    contact = db.query(DriverLicenseContact).filter(DriverLicenseContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.is_active = False
    
    # Also deactivate linked original record
    if contact.original_record_id:
        original = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id == contact.original_record_id
        ).first()
        if original:
            original.active_status = False

    db.commit()
    db.refresh(contact)
    return contact


def deactivate_fictitious(db: Session, fictitious_id: int):
    record = db.query(DriverLicenseFictitious).filter(DriverLicenseFictitious.id == fictitious_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
        
    record.is_active = False
    
    # Also deactivate linked original record
    if record.original_record_id:
        original = db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id == record.original_record_id
        ).first()
        if original:
            original.active_status = False

    db.commit()
    db.refresh(record)
    return record

# get by original id
def get_fictitious_records_by_original_id(db: Session, original_record_id: int):
    return db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.original_record_id == original_record_id,
        DriverLicenseFictitious.is_active == True
    ).all()


# get all global
def get_all_fictitious_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.is_active == True
    ).order_by(
        DriverLicenseFictitious.created_at.desc()
    ).offset(skip).limit(limit).all()

# get by id
def get_fictitious_record_by_id(db: Session, record_id: int):
    record = db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
        
    return record

# update
# update
def update_fictitious_record(db: Session, record_id: int, payload: DriverLicenseFictitiousUpdate, user_id: Optional[int] = None):
    record = db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(record, field, value)
        
    if user_id:
        record.updated_by = user_id
        
    db.commit()
    db.refresh(record)
    
    return record

# delete
def delete_fictitious_record(db: Session, record_id: int):
    record = db.query(DriverLicenseFictitious).filter(
        DriverLicenseFictitious.id == record_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
        
    db.delete(record)
    db.commit()
    
    return {"message": "Fictitious record deleted successfully"}
