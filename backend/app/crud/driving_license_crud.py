from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.driving_license import (
    DriverLicenseOriginalRecord,
    DriverLicenseContact,
    DriverLicenseFictitiousTrap
)
from app.schemas.driving_license_schema import (
    DriverLicenseOriginalCreate,
    DriverLicenseOriginalUpdate,
    DriverLicenseContactCreate,
    DriverLicenseFictitiousTrapCreate
)
from app.models.base import ActionType


# Create ops

# create main record
def create_original_record(db: Session, payload: DriverLicenseOriginalCreate):
    
    original = DriverLicenseOriginalRecord(
        status=payload.status,
        tln=payload.tln,
        tfn=payload.tfn,
        tdl=payload.tdl,
        fln=payload.fln,
        ffn=payload.ffn,
        fdl=payload.fdl,
        agency=payload.agency,
        contact=payload.contact,
        date_issued=payload.date_issued,
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
        alternative_contact4=payload.alternative_contact4
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact

# new fict trap record
def create_fictitious_trap(db: Session, original_record_id: int, payload: DriverLicenseFictitiousTrapCreate):

    #verify original record exists
    original = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.id == original_record_id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Original record not found")
    
    trap = DriverLicenseFictitiousTrap(
        original_record_id=original_record_id,
        date=payload.date,
        number=payload.number
    )
    
    db.add(trap)
    db.commit()
    db.refresh(trap)
    
    return trap

# Read OPs

# get all
def get_all_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    approval_status: Optional[str] = None,
    active_only: bool = True
):
    query = db.query(DriverLicenseOriginalRecord)
    
    # filters
    if active_only:
        query = query.filter(DriverLicenseOriginalRecord.active_status == True)
    
    if status:
        query = query.filter(DriverLicenseOriginalRecord.status == status)
    
    if approval_status:
        query = query.filter(DriverLicenseOriginalRecord.approval_status == approval_status)
    
    # order by most recent
    query = query.order_by(DriverLicenseOriginalRecord.created_at.desc())
    
    records = query.offset(skip).limit(limit).all()
    
    return records

# single record with all related record 
def get_record_by_id(db: Session, record_id: int):

    record = db.query(DriverLicenseOriginalRecord).options(
        joinedload(DriverLicenseOriginalRecord.contacts),
        joinedload(DriverLicenseOriginalRecord.fictitious_traps)
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
    """Get a driver license record by True Driver License"""
    
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
    db.query(DriverLicenseFictitiousTrap).filter(
        DriverLicenseFictitiousTrap.original_record_id == record_id
    ).delete()
    
    # Delete the original record
    db.delete(record)
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

# get al
def get_contacts_by_record(db: Session, record_id: int):
    
    contacts = db.query(DriverLicenseContact).filter(
        DriverLicenseContact.original_record_id == record_id
    ).all()
    
    return contacts

#update 
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
def get_traps_by_record(db: Session, record_id: int):
    
    traps = db.query(DriverLicenseFictitiousTrap).filter(
        DriverLicenseFictitiousTrap.original_record_id == record_id
    ).all()
    
    return traps

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
    pending_approval = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.approval_status == "pending"
    ).count()
    approved = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.approval_status == "approved"
    ).count()
    rejected = db.query(DriverLicenseOriginalRecord).filter(
        DriverLicenseOriginalRecord.approval_status == "rejected"
    ).count()
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "pending_approval": pending_approval,
        "approved": approved,
        "rejected": rejected
    }