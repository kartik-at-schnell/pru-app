from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.database import get_db
from app.models.vehicle_registration import VehicleRegistrationMaster

from app.crud.vehicle_registration_crud import (
    get_all_masters_for_dropdown,
    get_all_vehicles,
    get_vehicle_by_id,
    mark_fictitious_active,
    mark_fictitious_inactive,
    mark_undercover_active,
    mark_undercover_inactive,
    update_vehicle_record,
    delete_vehicle_record,
    get_vehicle_master_details,
    mark_active,
    mark_inactive,
    bulk_approve,
    bulk_reject,
    bulk_set_on_hold,
    bulk_activate,
    bulk_deactivate,
    bulk_delete,
    create_master_record,
    create_undercover_record,
    create_fictitious_record
)

from app.schemas.vehicle_registration_schema import(
    FictitiousCreateRequest,
    UnderCoverCreateRequest,
    VehicleRegistrationFictitious,
    VehicleRegistrationFictitiousResponse,
    VehicleRegistrationMasterCreate,
    VehicleRegistrationMasterBase,
    VehicleRegistrationMaster,
    VehicleRegistrationMasterDetails,
    BulkActionRequest,
    BulkActionResponse,
    VehicleRegistrationMasterResponse,
    VehicleRegistrationUnderCover,
    VehicleRegistrationUnderCoverResponse,
    MasterCreateRequest,
)
from app.security import get_current_user

from app.schemas.base_schema import ApiResponse
from app.models import user_models

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])

@router.post("/create")
def create_vehicle_record(
    record_type: str = Query(..., regex="^(master|undercover|fictitious)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    payload: Union[
        MasterCreateRequest,
        UnderCoverCreateRequest,
        FictitiousCreateRequest
    ] = Body(...)
):
    if record_type == "master":
        return create_master_record(db, payload)
    elif record_type == "undercover":
        return create_undercover_record(db, payload)
    elif record_type == "fictitious":
        return create_fictitious_record(db, payload)


# Read all
@router.get("/")
def list_vehicles(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    record_type: Optional[str] = Query(None, description="Filter: master, undercover, or fictitious"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, search=search, record_type=record_type)

        if record_type == "undercover":
            data = [VehicleRegistrationUnderCoverResponse.model_validate(v) for v in vehicle_list]
        elif record_type == "fictitious":
            data = [VehicleRegistrationFictitiousResponse.model_validate(v) for v in vehicle_list]
        else:
            data = [VehicleRegistrationMasterResponse.model_validate(v) for v in vehicle_list]
            
        return ApiResponse[List[type(data[0])]](data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records {e}")
    
# read PENDING
@router.get("/pending", response_model=ApiResponse[List[VehicleRegistrationMaster]])
def list_vehicles_pending(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, search=search, record_type=None, approval_status="pending")
        return ApiResponse[List[VehicleRegistrationMaster]](data=vehicle_list)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records {e}")
    

# read APPROVED
@router.get("/approved", response_model=ApiResponse[List[VehicleRegistrationMaster]])
def list_vehicles_approved(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, search=search, record_type=None, approval_status="approved")
        return ApiResponse[List[VehicleRegistrationMaster]](data=vehicle_list)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records {e}")


# read REJECTED
@router.get("/rejected", response_model=ApiResponse[List[VehicleRegistrationMaster]])
def list_vehicles_rejected(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, search=search, record_type=None, approval_status="rejected")
        return ApiResponse[List[VehicleRegistrationMaster]](data=vehicle_list)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records {e}")


# read ON HOLD
@router.get("/on-hold", response_model=ApiResponse[List[VehicleRegistrationMaster]])
def list_vehicles_on_hold(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, search=search, record_type=None, approval_status="on_hold")
        return ApiResponse[List[VehicleRegistrationMaster]](data=vehicle_list)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records {e}")

# Read one
# @router.get("/{record_id}", response_model=ApiResponse[VehicleRegistrationMaster])
# def get_vehicle(record_id: str, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
#     record = get_vehicle_by_id(db, record_id)
#     if not record:
#         raise HTTPException(status_code=404, detail="Vehicle record not found")
#     return ApiResponse[VehicleRegistrationMaster](data=record)

#update
@router.put("/{record_id}", response_model=ApiResponse[VehicleRegistrationMaster])
def update_vehicle(record_id: str, update_data: VehicleRegistrationMasterBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    return ApiResponse[VehicleRegistrationMaster](data=updated, message="Record updated successfully")

# # delete
# @router.delete("/{record_id}", response_model=ApiResponse)
# def delete_vehicle(record_id: str, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
#     deleted = delete_vehicle_record(db, record_id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Vehicle record not found")
#     return ApiResponse(message=f"Record ID {record_id} deleted successfully")

# mark inactive
@router.post("/{record_id}/inactive")
async def mark_inactive_route(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = mark_inactive(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"status": "marked inactive", "record_id": record_id}

# mark active
@router.post("/{record_id}/active")
async def mark_active_route(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = mark_active(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"status": "marked active", "record_id": record_id}


# Details endpoint
@router.get("/{master_id}/details", response_model=ApiResponse[VehicleRegistrationMasterDetails])
def get_master_record_details(master_id: str, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    db_record = get_vehicle_master_details(db=db, master_id=master_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Vehicle Master Record not found")
    return ApiResponse[VehicleRegistrationMasterDetails](data=db_record)

# new UC FC routes

# get dropdown of masters
@router.get("/masters/dropdown")
def get_masters_dropdown(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    masters = get_all_masters_for_dropdown(db)
    return [{"id": m[0], "vin": m[1], "owner": m[2]} for m in masters]


# Undercover

@router.post("/undercover/create")
def create_undercover_route(
    payload: UnderCoverCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    master = db.query(VehicleRegistrationMaster).filter_by(id=payload.master_record_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master record not found")

    uc = VehicleRegistrationUnderCover(
        master_record_id=master.id,
        vehicle_id_number=master.vehicle_id_number,
        **payload.model_dump(exclude={"master_record_id"})
    )

    db.add(uc)
    db.commit()
    db.refresh(uc)

    return {
        "id": uc.id,
        "license_number": uc.license_number,
        "vehicle_id_number": uc.vehicle_id_number,
        "master_id": uc.master_record_id
    }

# @router.get("/undercover/master/{master_id}")
# def get_uc_by_master(
#     master_id: str,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     records = get_undercover_by_master(db, master_id)
#     return {"master_id": master_id, "count": len(records), "records": records}

# @router.post("/undercover/{uc_id}/mark-active")
# def mark_uc_active(
#     uc_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     mark_undercover_active(db, uc_id)
#     return {"status": "marked active", "uc_id": uc_id}

# @router.post("/undercover/{uc_id}/mark-inactive")
# def mark_uc_inactive(
#     uc_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     mark_undercover_inactive(db, uc_id)
#     return {"status": "marked inactive", "uc_id": uc_id}


# Fictitious

@router.post("/fictitious/create")
def create_fictitious_route(
    payload: FictitiousCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    master = db.query(VehicleRegistrationMaster).filter_by(id=payload.master_record_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master record not found")

    fc = VehicleRegistrationFictitious(
        master_record_id=master.id,
        vehicle_id_number=master.vehicle_id_number,
        **payload.model_dump(exclude={"master_record_id"})
    )

    db.add(fc)
    db.commit()
    db.refresh(fc)
    return {
        "id": fc.id,
        "license_number": fc.license_number,
        "vehicle_id_number": fc.vehicle_id_number,
        "master_id": fc.master_record_id
    }


# @router.get("/fictitious/master/{master_id}")
# def get_fc_by_master(
#     master_id: str,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     records = get_fictitious_by_master(db, master_id)
#     return {"master_id": master_id, "count": len(records), "records": records}

# @router.post("/fictitious/{fc_id}/mark-active")
# def mark_fc_active(
#     fc_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     mark_fictitious_active(db, fc_id)
#     return {"status": "marked active", "fc_id": fc_id}

# @router.post("/fictitious/{fc_id}/mark-inactive")
# def mark_fc_inactive(
#     fc_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     mark_fictitious_inactive(db, fc_id)
#     return {"status": "marked inactive", "fc_id": fc_id}

# bulk actions routes

#bulk approve
@router.post("/bulk-approve", response_model=ApiResponse[BulkActionResponse])
def bulk_approve_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_approve(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully approved {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

# bulk reject
@router.post("/bulk-reject", response_model=ApiResponse[BulkActionResponse])
def bulk_reject_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_reject(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully rejected {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

# bulk on-hold
@router.post("/bulk-on-hold", response_model=ApiResponse[BulkActionResponse])
def bulk_on_hold_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_set_on_hold(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully set {updated_count} records to on-hold"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

#bulk flag active
@router.post("/bulk-activate", response_model=ApiResponse[BulkActionResponse])
def bulk_activate_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_activate(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully activated {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

 # bulk flag inactive
@router.post("/bulk-deactivate", response_model=ApiResponse[BulkActionResponse])
def bulk_deactivate_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated_count = bulk_deactivate(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=updated_count,
        failed_count=len(request.record_ids) - updated_count,
        message=f"Successfully deactivated {updated_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

# bulk delete
@router.delete("/bulk-delete", response_model=ApiResponse[BulkActionResponse])
def bulk_delete_route(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    deleted_count = bulk_delete(db, request.record_ids)
    
    response_data = BulkActionResponse(
        success_count=deleted_count,
        failed_count=len(request.record_ids) - deleted_count,
        message=f"Successfully deleted {deleted_count} records"
    )
    return ApiResponse[BulkActionResponse](data=response_data)

