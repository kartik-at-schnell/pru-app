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
    RecordsCountResponse,
    DriverLicenseFictitiousCreate,
    DriverLicenseFictitiousUpdate,
    DriverLicenseFictitiousResponse
)

from app.schemas.base_schema import ApiResponse
from app.models import user_models
from app.rbac import PermissionChecker, RoleChecker

router = APIRouter(prefix="/driver-license", tags=["Driver License"])

# Main endpoints
# crreate new
@router.post("/create", response_model=DriverLicenseOriginalResponse)
def create_original_record(
    payload: DriverLicenseOriginalCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:create_original"))
):
    try:
        record = crud.create_original_record(db, payload)
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# get all records
@router.get("/", response_model=ApiResponse[List[DriverLicenseOriginalResponse]])
def get_all_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    approval_status: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_list"))
):
    records = crud.get_all_records(
        db=db,
        skip=skip,
        limit=limit,
        # status=status,
        approval_status=approval_status,
        active_only=active_only
    )
    return ApiResponse(
        status="success",
        message=f"Retrieved {len(records)} driver license records",
        data=records
    )

# get detailed record
@router.get("/{record_id}", response_model=DriverLicenseOriginalDetailResponse)
def get_record_by_id(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    record = crud.get_record_by_id(db, record_id)
    return record

# get by true dl
@router.get("/tdl/{tdl}", response_model=DriverLicenseOriginalDetailResponse)
def get_record_by_tdl(
    tdl: str,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:search"))
):
    record = crud.get_record_by_tdl(db, tdl)
    return record

# upadate
@router.put("/{record_id}", response_model=DriverLicenseOriginalResponse)
def update_original_record(
    record_id: int,
    payload: DriverLicenseOriginalUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    record = crud.update_original_record(db, record_id, payload)
    return record

# soft delet / flag inactive
@router.delete("/{record_id}", response_model=DeleteResponse)
def soft_delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    result = crud.soft_delete_record(db, record_id)
    return result

# restre/ flag active
@router.post("/{record_id}/restore", response_model=DriverLicenseOriginalResponse)
def restore_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    record = crud.restore_record(db, record_id)
    return record

# hard delete
@router.delete("/{record_id}/permanent", response_model=DeleteResponse)
def hard_delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    result = crud.hard_delete_record(db, record_id)
    return result

# CONTACT
# global get all
@router.get("/contacts/all", response_model=ApiResponse[List[DriverLicenseContactResponse]])
def get_all_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_list"))
):
    contacts = crud.get_all_contacts(db, skip=skip, limit=limit)
    return ApiResponse(
        status="success",
        message=f"Retrieved {len(contacts)} contacts",
        data=contacts
    )

# get one by id
@router.get("/contact/{contact_id}", response_model=ApiResponse[DriverLicenseContactResponse])
def get_contact_by_id(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    contact = crud.get_contact_by_id(db, contact_id)
    return ApiResponse(
        status="success",
        message="Contact retrieved successfully",
        data=contact
    )

# new
@router.post("/{record_id}/contact", response_model=DriverLicenseContactResponse)
def create_contact(
    record_id: int,
    payload: DriverLicenseContactCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    contact = crud.create_contact(db, record_id, payload)
    return contact

# get all fro specific record
@router.get("/{record_id}/contacts", response_model=List[DriverLicenseContactResponse])
def get_contacts_by_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    contacts = crud.get_contacts_by_record(db, record_id)
    return contacts

# update
@router.put("/contact/{contact_id}/update", response_model=DriverLicenseContactResponse)
def update_contact(
    contact_id: int,
    payload: DriverLicenseContactCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    contact = crud.update_contact(db, contact_id, payload)
    return contact

# delete
@router.delete("/contact/{contact_id}/delete", response_model=DeleteResponse)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    result = crud.delete_contact(db, contact_id)
    return result

# FICTITIOUS TRAP
# get all, global
@router.get("/traps/all", response_model=ApiResponse[List[DriverLicenseFictitiousTrapResponse]])
def get_all_traps(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_list"))
):
    traps = crud.get_all_traps(db, skip=skip, limit=limit)
    return ApiResponse(
        status="success",
        message=f"Retrieved {len(traps)} fictitious traps",
        data=traps
    )

# get single
@router.get("/trap/{trap_id}", response_model=ApiResponse[DriverLicenseFictitiousTrapResponse])
def get_trap_by_id(
    trap_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    trap = crud.get_trap_by_id(db, trap_id)
    return ApiResponse(
        status="success",
        message="Fictitious trap retrieved successfully",
        data=trap
    )

# record-specific trap endpoints
# create
@router.post("/{fictitious_record_id}/trap", response_model=DriverLicenseFictitiousTrapResponse)
def create_fictitious_trap(
    fictitious_record_id: int,
    payload: DriverLicenseFictitiousTrapCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    trap = crud.create_fictitious_trap(db, fictitious_record_id, payload)
    return trap

# get all
@router.get("/{fictitious_record_id}/traps", response_model=List[DriverLicenseFictitiousTrapResponse])
def get_traps_by_fictitious_record(
    fictitious_record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    traps = crud.get_traps_by_fictitious_record(db, fictitious_record_id)
    return traps

# update
@router.put("/trap/{trap_id}/update", response_model=DriverLicenseFictitiousTrapResponse)
def update_trap(
    trap_id: int,
    payload: DriverLicenseFictitiousTrapCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    trap = crud.update_trap(db, trap_id, payload)
    return trap

# delete
@router.delete("/trap/{trap_id}/delete", response_model=DeleteResponse)
def delete_trap(
    trap_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    result = crud.delete_trap(db, trap_id)
    return result


# FICTITIOUS RECORD (New)

# create
@router.post("/{record_id}/fictitious", response_model=DriverLicenseFictitiousResponse)
def create_fictitious_record(
    record_id: int,
    payload: DriverLicenseFictitiousCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:create_fictitious"))
):
    record = crud.create_fictitious_record(db, record_id, payload)
    return record

# get all by original record
@router.get("/{record_id}/fictitious", response_model=List[DriverLicenseFictitiousResponse])
def get_fictitious_records_by_original(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    records = crud.get_fictitious_records_by_original_id(db, record_id)
    return records

# get by id
@router.get("/fictitious/{record_id}", response_model=DriverLicenseFictitiousResponse)
def get_fictitious_record_by_id(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("dl:view_details"))
):
    record = crud.get_fictitious_record_by_id(db, record_id)
    return record

# update
@router.put("/fictitious/{record_id}/update", response_model=DriverLicenseFictitiousResponse)
def update_fictitious_record(
    record_id: int,
    payload: DriverLicenseFictitiousUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    record = crud.update_fictitious_record(db, record_id, payload)
    return record

# delete
@router.delete("/fictitious/{record_id}/delete", response_model=DeleteResponse)
def delete_fictitious_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("dl:edit"))
):
    result = crud.delete_fictitious_record(db, record_id)
    return result


# stats
@router.get("/stats/count", response_model=RecordsCountResponse)
def get_records_count(db: Session = Depends(get_db)):
    stats = crud.get_records_count(db)
    return stats
