from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.database import get_db

from app.crud.vehicle_registration_crud import (
    create_master_record,
    create_undercover_record,
    create_fictitious_record,
    get_all_masters_for_dropdown,
    get_all_vehicles,
    get_vehicle_master_details,
    update_vehicle_record
)

from app.schemas.vehicle_registration_schema import(
    FictitiousCreateRequest,
    UnderCoverCreateRequest,
    VehicleRegistrationFictitiousResponse,
    VehicleRegistrationMasterBase,
    VehicleRegistrationMasterDetails,
    VehicleRegistrationMasterResponse,
    VehicleRegistrationUnderCoverResponse,
    MasterCreateRequest,
)
from app.security import get_current_user

from app.schemas.base_schema import ApiResponse
from app.models import user_models

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])
    
# create new records
@router.post("/create", response_model=ApiResponse[Union[
    VehicleRegistrationMasterResponse, 
    VehicleRegistrationUnderCoverResponse, 
    VehicleRegistrationFictitiousResponse
]])
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
    try:
        if record_type == "master":
            result = create_master_record(db, payload)
            data = VehicleRegistrationMasterResponse.model_validate(result)
            return ApiResponse(
                status="success",
                message=f"Master record created successfully with ID {result.id}",
                data=data
            )
        elif record_type == "undercover":
            result = create_undercover_record(db, payload)
            data = VehicleRegistrationUnderCoverResponse.model_validate(result)
            return ApiResponse(
                status="success",
                message=f"Undercover record created successfully with ID {result.id}",
                data=data
            )
        elif record_type == "fictitious":
            result = create_fictitious_record(db, payload)
            data = VehicleRegistrationFictitiousResponse.model_validate(result)
            return ApiResponse(
                status="success",
                message=f"Fictitious record created successfully with ID {result.id}",
                data=data
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create record: {str(e)}"
        )
    
# Read all
@router.get("/", response_model=ApiResponse[List[Union[
    VehicleRegistrationMasterResponse,
    VehicleRegistrationUnderCoverResponse,
    VehicleRegistrationFictitiousResponse
]]])
def list_vehicles(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = Query(None, description="Search by license number"),
    record_type: Optional[str] = Query(None, description="master, undercover, or fictitious"),
    approval_status: Optional[str] = Query(None, description="pending, approved, rejected, on_hold"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(
            db, skip=skip, limit=limit, search=search,
            record_type=record_type, approval_status=approval_status
        )

        if record_type == "undercover":
            data = [VehicleRegistrationUnderCoverResponse.model_validate(v) for v in vehicle_list]
        elif record_type == "fictitious":
            data = [VehicleRegistrationFictitiousResponse.model_validate(v) for v in vehicle_list]
        else:
            data = [VehicleRegistrationMasterResponse.model_validate(v) for v in vehicle_list]

        return ApiResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records: {e}")


#update
router.put("/{record_id}", response_model=ApiResponse[VehicleRegistrationMasterResponse])
def update_vehicle(
    record_id: int,  # Changed from str to int
    update_data: VehicleRegistrationMasterBase,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    
    data = VehicleRegistrationMasterResponse.model_validate(updated)
    return ApiResponse(
        status="success",
        message=f"Record {record_id} updated successfully",
        data=data)
    

# Details endpoint
@router.get("/{master_id}/details", response_model=ApiResponse[VehicleRegistrationMasterDetails])
def get_master_record_details(master_id: str, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    db_record = get_vehicle_master_details(db=db, master_id=master_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Vehicle Master Record not found")
    return ApiResponse[VehicleRegistrationMasterDetails](data=db_record)

# get dropdown of masters
@router.get("/masters/dropdown")
def get_masters_dropdown(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    masters = get_all_masters_for_dropdown(db)
    return [{"id": m[0], "vin": m[1], "owner": m[2]} for m in masters]
