from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from app.database import get_db
from app.api.dependencies.rbac import require_role
from app.crud.vehicle_registration_crud import (
    create_master_record,
    create_undercover_record,
    create_fictitious_record,
    get_all_masters_for_dropdown,
    get_all_vehicles,
    get_vehicle_master_details,
    update_vehicle_record,
)

from app.schemas.vehicle_registration_schema import (
    FictitiousCreateRequest,
    UnderCoverCreateRequest,
    VehicleRegistrationFictitiousResponse,
    VehicleRegistrationMasterBase,
    VehicleRegistrationMasterDetails,
    VehicleRegistrationMasterResponse,
    VehicleRegistrationUnderCoverResponse,
    MasterCreateRequest,
)

from app.schemas.base_schema import ApiResponse

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])


# ---------------- CREATE (admin only) ------------------
@router.post(
    "/create",
    dependencies=[Depends(require_role("admin"))],  # FIXED
    response_model=ApiResponse[Union[
        VehicleRegistrationMasterResponse,
        VehicleRegistrationUnderCoverResponse,
        VehicleRegistrationFictitiousResponse
    ]]
)
def create_vehicle_record(
    record_type: str = Query(..., regex="^(master|undercover|fictitious)$"),
    db: Session = Depends(get_db),
    payload: Union[
        MasterCreateRequest,
        UnderCoverCreateRequest,
        FictitiousCreateRequest
    ] = Body(...)
):

    if record_type == "master":
        result = create_master_record(db, payload)
        return ApiResponse(
            status="success",
            message=f"Master record created with ID {result.id}",
            data=VehicleRegistrationMasterResponse.model_validate(result)
        )

    elif record_type == "undercover":
        result = create_undercover_record(db, payload)
        return ApiResponse(
            status="success",
            message=f"Undercover record created with ID {result.id}",
            data=VehicleRegistrationUnderCoverResponse.model_validate(result)
        )

    elif record_type == "fictitious":
        result = create_fictitious_record(db, payload)
        return ApiResponse(
            status="success",
            message=f"Fictitious record created with ID {result.id}",
            data=VehicleRegistrationFictitiousResponse.model_validate(result)
        )


# ---------------- LIST (admin + operator) ------------------
@router.get(
    "/", 
    dependencies=[Depends(require_role("admin", "operator"))], 
    response_model=ApiResponse[List[Union[
        VehicleRegistrationMasterResponse,
        VehicleRegistrationUnderCoverResponse,
        VehicleRegistrationFictitiousResponse
    ]]]
)
def list_vehicles(
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = None,
    record_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db)
):

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


# ---------------- UPDATE (admin + operator) ------------------
@router.put(
    "/{record_id}",
    dependencies=[Depends(require_role("admin", "operator"))],  # FIXED
    response_model=ApiResponse[VehicleRegistrationMasterResponse]
)
def update_vehicle(
    record_id: int,
    update_data: VehicleRegistrationMasterBase,
    db: Session = Depends(get_db)
):

    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(404, "Vehicle record not found")

    return ApiResponse(
        status="success",
        message=f"Record {record_id} updated successfully",
        data=VehicleRegistrationMasterResponse.model_validate(updated)
    )


# ---------------- DETAILS ------------------
@router.get(
    "/{master_id}/details",
    dependencies=[Depends(require_role("admin", "operator"))],  # FIXED
    response_model=ApiResponse[VehicleRegistrationMasterDetails]
)
def get_master_record_details(
    master_id: str,
    db: Session = Depends(get_db)
):

    db_record = get_vehicle_master_details(db=db, master_id=master_id)

    if db_record is None:
        raise HTTPException(404, "Vehicle Master Record not found")

    return ApiResponse(data=db_record)


# ---------------- DROPDOWN ------------------
@router.get(
    "/masters/dropdown",
    dependencies=[Depends(require_role("admin", "operator"))]  # FIXED
)
def get_masters_dropdown(
    db: Session = Depends(get_db)
):

    masters = get_all_masters_for_dropdown(db)
    return [{"id": m[0], "vin": m[1], "owner": m[2]} for m in masters]
