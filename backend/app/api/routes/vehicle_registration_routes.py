from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app import crud
from app.crud.vehicle_registration_crud import get_all_contacts, get_contacts_by_master
from app.crud.vehicle_registration_crud import  create_vr_contact, delete_vr_reciprocal_received, get_all_reciprocal_records, get_all_vr_reciprocal_received, update_vr_reciprocal_received
from app.crud.vehicle_registration_crud import get_reciprocal_record_by_id
from app.crud.vehicle_registration_crud import update_reciprocal_record 
from app.crud.vehicle_registration_crud import delete_reciprocal_record
from app.schemas.vehicle_registration_schema import VRContactUpdate, VehicleRegistrationReciprocalIssuedUpdate
from app.schemas.vehicle_registration_schema import (
    VRReciprocalReceivedCreate,
    VRReciprocalReceivedResponse,
    VRReciprocalReceivedUpdate,
    VRContactCreate,
    VRContactResponse,
    
)
from app.crud.vehicle_registration_crud import create_vr_reciprocal_received

from app.database import get_db
from app.api.dependencies.rbac import require_role

# CRUD Imports
from app.crud.vehicle_registration_crud import (
    create_master_record,
    create_undercover_record,
    create_fictitious_record,
    create_reciprocal_issued_record, # Ensure this is imported
    get_reciprocal_record_by_id,
    get_all_masters_for_dropdown,
    get_all_vehicles,
    get_vehicle_master_details,
    update_vehicle_record,
    
)

# Schema Imports
from app.schemas.vehicle_registration_schema import (
    # Create Request Schemas
    MasterCreateRequest,
    UnderCoverCreateRequest,
    FictitiousCreateRequest,
    VehicleRegistrationReciprocalIssuedCreateBody,
    
    # Response Schemas
    VehicleRegistrationMasterResponse,
    VehicleRegistrationUnderCoverResponse,
    VehicleRegistrationFictitiousResponse,
    VehicleRegistrationReciprocalIssuedResponse, # Make sure you added this to your schema file
    VehicleRegistrationMasterBase,
    VehicleRegistrationMasterDetails,

)

from app.schemas.base_schema import ApiResponse

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])


# ---------------- CREATE GENERIC (Master, Undercover, Fictitious) ------------------
@router.post(
    "/create",
    dependencies=[Depends(require_role("admin"))],
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
    
    # 'reciprocal' logic removed from here to use the separate endpoint below


# ---------------- CREATE RECIPROCAL (Separate Endpoint) ------------------
@router.post(
    "/reciprocal",
   # dependencies=[Depends(require_role("admin"))],
    response_model=ApiResponse[VehicleRegistrationReciprocalIssuedResponse]
)
def create_reciprocal_record(
    payload: VehicleRegistrationReciprocalIssuedCreateBody,
    db: Session = Depends(get_db)
):
    """
    Dedicated endpoint to create a Reciprocal Issued record.
    """
    result = create_reciprocal_issued_record(db, payload)
    
    return ApiResponse(
        status="success",
        message=f"Reciprocal record created with ID {result.id}",
        data=VehicleRegistrationReciprocalIssuedResponse.model_validate(result)
    )

# READ Endpoint (Get One)
@router.get(
    "/reciprocal/{record_id}",
   # dependencies=[Depends(require_role("admin", "operator"))],
    response_model=ApiResponse[VehicleRegistrationReciprocalIssuedResponse]
)
def get_reciprocal(
    record_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get details of a specific Reciprocal Issued record.
    """
    record = get_reciprocal_record_by_id(db, record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Reciprocal record not found")
        
    return ApiResponse(
        data=VehicleRegistrationReciprocalIssuedResponse.model_validate(record)
    )


@router.get(
    "/reciprocal/list",
    #dependencies=[Depends(require_role("admin", "operator"))],
    response_model=ApiResponse[List[VehicleRegistrationReciprocalIssuedResponse]]
)
def list_reciprocal_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get a list of all Reciprocal Issued records.
    """
    records = get_all_reciprocal_records(db, skip=skip, limit=limit)
    
    # Convert list of DB objects to list of Pydantic schemas
    data = [VehicleRegistrationReciprocalIssuedResponse.model_validate(r) for r in records]
    
    return ApiResponse(
        status="success",
        message=f"Found {len(data)} records",
        data=data
    )

@router.delete(
    "/reciprocal/{record_id}",
    dependencies=[Depends(require_role("admin"))],
    response_model=ApiResponse[dict]
)
def delete_reciprocal(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific Reciprocal Issued record.
    """
    delete_reciprocal_record(db, record_id)

    return ApiResponse(
        status="success",
        message=f"Reciprocal record {record_id} deleted successfully",
        data={"id": record_id}
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

@router.put(
    "/reciprocal/{record_id}",
  #  dependencies=[Depends(require_role("admin"))],
    response_model=ApiResponse[VehicleRegistrationReciprocalIssuedResponse]
)
def update_reciprocal(
    record_id: int,
    payload: VehicleRegistrationReciprocalIssuedUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing Reciprocal Issued record.
    """
    updated = update_reciprocal_record(db, record_id, payload)

    return ApiResponse(
        status="success",
        message=f"Reciprocal record {record_id} updated successfully",
        data=VehicleRegistrationReciprocalIssuedResponse.model_validate(updated)
    )


# ---------------- UPDATE (admin + operator) ------------------
@router.put(
    "/{record_id}",
 #   dependencies=[Depends(require_role("admin", "operator"))],
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
  #  dependencies=[Depends(require_role("admin", "operator"))],
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
   # dependencies=[Depends(require_role("admin", "operator"))]
)
def get_masters_dropdown(
    db: Session = Depends(get_db)
):
    masters = get_all_masters_for_dropdown(db)
    return [{"id": m[0], "vin": m[1], "owner": m[2]} for m in masters]


@router.post(
    "/reciprocal-received",
    response_model=VRReciprocalReceivedResponse
)
def create_reciprocal_received(
    payload: VRReciprocalReceivedCreate,
    db: Session = Depends(get_db)
):
    record = create_vr_reciprocal_received(db, payload)
    return VRReciprocalReceivedResponse.model_validate(record)

@router.get(
    "/reciprocal-received",
    response_model=List[VRReciprocalReceivedResponse]
)
def list_reciprocal_received(db: Session = Depends(get_db)):
    records = get_all_vr_reciprocal_received(db)
    return [VRReciprocalReceivedResponse.model_validate(r) for r in records]

@router.put(
    "/reciprocal-received/{record_id}",
    response_model=VRReciprocalReceivedResponse
)
def update_reciprocal_received(
    record_id: int,
    payload: VRReciprocalReceivedUpdate,
    db: Session = Depends(get_db)
):
    record = update_vr_reciprocal_received(db, record_id, payload)
    return VRReciprocalReceivedResponse.model_validate(record)

@router.delete(
    "/reciprocal-received/{record_id}",
    status_code=204
)
def delete_reciprocal_received(
    record_id: int,
    db: Session = Depends(get_db)
):
    delete_vr_reciprocal_received(db, record_id)
    return

@router.post(
    "/contact",
    response_model=VRContactResponse
)
def create_contact(
    payload: VRContactCreate,
    db: Session = Depends(get_db)
):
    record = create_vr_contact(db, payload)
    return VRContactResponse.model_validate(record)

@router.get("/contacts", response_model=List[VRContactResponse])
def list_all_contacts(db: Session = Depends(get_db)):
    return get_all_contacts(db)


@router.get("/contacts/{master_record_id}", response_model=List[VRContactResponse])
def list_contacts_by_master(master_record_id: int, db: Session = Depends(get_db)):
    contacts = get_contacts_by_master(db, master_record_id)
    
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found for this master_record_id")

    return contacts
@router.put("/contacts/{contact_id}", response_model=VRContactResponse)
def update_contact_route(
    contact_id: int,
    payload: VRContactUpdate,
    db: Session = Depends(get_db)
):
    from app.crud.vehicle_registration_crud import update_contact as update_contact_crud

    updated = update_contact_crud(db, contact_id, payload)

    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")

    return VRContactResponse.model_validate(updated)

