from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud import driving_license_crud as crud
from app.schemas.driving_license_schema import (
    DriverLicenseOriginalCreate,
    DriverLicenseOriginalUpdate,
    DriverLicenseOriginalResponse,
    DriverLicenseOriginalDetailResponse,
    DriverLicenseContactCreate,
    DriverLicenseContactResponse,
    DriverLicenseFictitiousTrapCreate,
    DriverLicenseFictitiousTrapResponse,
    ApprovalStatusUpdate,
    DeleteResponse,
    RecordsCountResponse
)

router = APIRouter(prefix="/driver-license", tags=["Driver License"])


# Main record endpoints

# crreate new
@router.post("/create", response_model=DriverLicenseOriginalResponse)
def create_original_record(
    payload: DriverLicenseOriginalCreate,
    db: Session = Depends(get_db)
):
    try:
        record = crud.create_original_record(db, payload)
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# get all records
@router.get("/", response_model=List[DriverLicenseOriginalResponse])
def get_all_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    approval_status: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    records = crud.get_all_records(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        approval_status=approval_status,
        active_only=active_only
    )
    return records

# get by id, with all related records
@router.get("/{record_id}", response_model=DriverLicenseOriginalDetailResponse)
def get_record_by_id(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = crud.get_record_by_id(db, record_id)
    return record

# get record by True Driver License
@router.get("/tdl/{tdl}", response_model=DriverLicenseOriginalDetailResponse)
def get_record_by_tdl(
    tdl: str,
    db: Session = Depends(get_db)
):
    record = crud.get_record_by_tdl(db, tdl)
    return record

# update
@router.put("/{record_id}", response_model=DriverLicenseOriginalResponse)
def update_original_record(
    record_id: int,
    payload: DriverLicenseOriginalUpdate,
    db: Session = Depends(get_db)
):
    record = crud.update_original_record(db, record_id, payload)
    return record

# soft delete/flag inactive
@router.delete("/{record_id}", response_model=DeleteResponse)
def soft_delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    result = crud.soft_delete_record(db, record_id)
    return result

@router.post("/{record_id}/restore", response_model=DriverLicenseOriginalResponse)
def restore_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = crud.restore_record(db, record_id)
    return record

# hard delete
@router.delete("/{record_id}/permanent", response_model=DeleteResponse)
def hard_delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    result = crud.hard_delete_record(db, record_id)
    return result


# CONTACT 

# create
@router.post("/{record_id}/contact", response_model=DriverLicenseContactResponse)
def create_contact(
    record_id: int,
    payload: DriverLicenseContactCreate,
    db: Session = Depends(get_db)
):
    contact = crud.create_contact(db, record_id, payload)
    return contact

# get all contact of a dl
@router.get("/{record_id}/contacts", response_model=List[DriverLicenseContactResponse])
def get_contacts(
    record_id: int,
    db: Session = Depends(get_db)
):
    contacts = crud.get_contacts_by_record(db, record_id)
    return contacts

# update
@router.put("/contact/{contact_id}", response_model=DriverLicenseContactResponse)
def update_contact(
    contact_id: int,
    payload: DriverLicenseContactCreate,
    db: Session = Depends(get_db)
):
    contact = crud.update_contact(db, contact_id, payload)
    return contact

# delete
@router.delete("/contact/{contact_id}", response_model=DeleteResponse)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    result = crud.delete_contact(db, contact_id)
    return result


# fictitious endpoints

# create
@router.post("/{record_id}/trap", response_model=DriverLicenseFictitiousTrapResponse)
def create_fictitious_trap(
    record_id: int,
    payload: DriverLicenseFictitiousTrapCreate,
    db: Session = Depends(get_db)
):
    trap = crud.create_fictitious_trap(db, record_id, payload)
    return trap

# get all
@router.get("/{record_id}/traps", response_model=List[DriverLicenseFictitiousTrapResponse])
def get_traps(
    record_id: int,
    db: Session = Depends(get_db)
):
    traps = crud.get_traps_by_record(db, record_id)
    return traps

# delete
@router.delete("/trap/{trap_id}", response_model=DeleteResponse)
def delete_trap(
    trap_id: int,
    db: Session = Depends(get_db)
):
    result = crud.delete_trap(db, trap_id)
    return result


# stat endpoint, will add more later

@router.get("/stats/count", response_model=RecordsCountResponse)
def get_records_count(db: Session = Depends(get_db)):
    stats = crud.get_records_count(db)
    return stats