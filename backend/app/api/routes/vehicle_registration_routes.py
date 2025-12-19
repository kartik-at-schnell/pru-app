from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.database import get_db

from app.crud.vehicle_registration_crud import (
    create_contact,
    create_master_record,
    create_reciprocal_issued,
    create_reciprocal_received,
    create_trap_info_fictitious,
    create_trap_info_undercover,
    create_undercover_record,
    create_fictitious_record,
    delete_reciprocal_issued,
    delete_reciprocal_received,
    delete_trap_info_fictitious,
    delete_trap_info_undercover,
    get_all_contacts,
    get_all_masters_for_dropdown,
    get_all_reciprocal_issued,
    get_all_reciprocal_received,
    get_all_trap_info_fictitious,
    get_all_trap_info_undercover,
    get_all_vehicles,
    get_contact,
    get_contacts_by_master,
    get_master_by_id,
    get_reciprocal_issued,
    get_reciprocal_issued_by_id,
    get_reciprocal_issued_by_master,
    get_reciprocal_received,
    get_reciprocal_received_by_master,
    get_trap_info_fictitious,
    get_trap_info_fictitious_by_fc,
    get_trap_info_undercover,
    get_trap_info_undercover_by_uc,
    get_vehicle_master_details,
    update_reciprocal_issued,
    update_reciprocal_received,
    update_trap_info_fictitious,
    update_trap_info_undercover,
    update_vehicle_record
)

from app.schemas.vehicle_registration_schema import(
    FictitiousCreateRequest,
    UnderCoverCreateRequest,
    VehicleRegistrationContact,
    VehicleRegistrationContactCreateBody,
    VehicleRegistrationFictitiousResponse,
    VehicleRegistrationFictitiousTrapInfo,
    VehicleRegistrationFictitiousTrapInfoCreateBody,
    VehicleRegistrationMasterBase,
    VehicleRegistrationMasterDetails,
    VehicleRegistrationMasterResponse,
    VehicleRegistrationReciprocalIssued,
    VehicleRegistrationReciprocalIssuedCreateBody,
    VehicleRegistrationReciprocalReceived,
    VehicleRegistrationReciprocalReceivedCreateBody,
    VehicleRegistrationUnderCoverResponse,
    MasterCreateRequest,
    VehicleRegistrationUnderCoverTrapInfo,
    VehicleRegistrationUnderCoverTrapInfoCreateBody,
    VehicleRegistrationMasterUpdate,
    VehicleRegistrationUnderCoverUpdate,
    VehicleRegistrationFictitiousUpdate,
)
from app.security import get_current_user

from app.schemas.base_schema import ApiResponse
from app.models import user_models
from app.crud.driving_license_crud import delete_contact, update_contact
from app.rbac import PermissionChecker, RoleChecker

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
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:create")),
    payload: dict = Body(...)
):
    try:
        if record_type == "master":
            # Validate payload as Master
            validated_payload = MasterCreateRequest(**payload)
            result = create_master_record(db, validated_payload)
            data = VehicleRegistrationMasterResponse.model_validate(result)
            return ApiResponse(
                status="success",
                message=f"Master record created successfully with ID {result.id}",
                data=data
            )
        elif record_type == "undercover":
            validated_payload = UnderCoverCreateRequest(**payload)
            result = create_undercover_record(db, validated_payload)
            data = VehicleRegistrationUnderCoverResponse.model_validate(result)
            return ApiResponse(
                status="success",
                message=f"Undercover record created successfully with ID {result.id}",
                data=data
            )
        elif record_type == "fictitious":
            validated_payload = FictitiousCreateRequest(**payload)
            result = create_fictitious_record(db, validated_payload)
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
    # current_user: user_models.User = Depends(get_current_user)
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager","User")),
    permission_check = Depends(PermissionChecker("vr:view_list")),
    
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
@router.put("/{record_id}", response_model=ApiResponse[VehicleRegistrationMasterResponse])
def update_vehicle(
    record_id: str,  # Changed from str to int
    update_data: VehicleRegistrationMasterUpdate,
    db: Session = Depends(get_db),
    #current_user: user_models.User = Depends(get_current_user)
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    
    data = VehicleRegistrationMasterResponse.model_validate(updated)
    return ApiResponse(
        status="success",
        message=f"Record {record_id} updated successfully",
        data=data)
    

@router.put("/undercover/{record_id}", response_model=ApiResponse[VehicleRegistrationUnderCoverResponse])
def update_undercover_vehicle(
    record_id: str,
    update_data: VehicleRegistrationUnderCoverUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    updated = update_vehicle_record(db, record_id, update_data, record_type="undercover")
    if not updated:
        raise HTTPException(status_code=404, detail="Undercover record not found")
    
    data = VehicleRegistrationUnderCoverResponse.model_validate(updated)
    return ApiResponse(
        status="success",
        message=f"Undercover record {record_id} updated successfully",
        data=data)
    

@router.put("/fictitious/{record_id}", response_model=ApiResponse[VehicleRegistrationFictitiousResponse])
def update_fictitious_vehicle(
    record_id: str,
    update_data: VehicleRegistrationFictitiousUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    updated = update_vehicle_record(db, record_id, update_data, record_type="fictitious")
    if not updated:
        raise HTTPException(status_code=404, detail="Fictitious record not found")
    
    data = VehicleRegistrationFictitiousResponse.model_validate(updated)
    return ApiResponse(
        status="success",
        message=f"Fictitious record {record_id} updated successfully",
        data=data)
    

# Details endpoint
@router.get("/{master_id}/details", response_model=ApiResponse[VehicleRegistrationMasterDetails])
def get_master_record_details(master_id: str, db: Session = Depends(get_db), 
                              #current_user: user_models.User = Depends(get_current_user)
                                current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
                                permission_check = Depends(PermissionChecker("vr:view_details")),
                              
                              ):
    db_record = get_vehicle_master_details(db=db, master_id=master_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Vehicle Master Record not found")
    return ApiResponse[VehicleRegistrationMasterDetails](data=db_record)

# Get VIN by ID (RBAC with email)
@router.get("/vin/{record_id}")
def get_vin_by_id(
    record_id: int,
    email: str = Query(..., description="User email for verification"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details"))
):
    try:
        master = get_master_by_id(db, record_id)
        
        # We could add specific logic for 'email' here if needed, 
        # e.g., verifying it matches current_user or logging it. 
        # For now, we accept it as requested for the definition.

        return ApiResponse(
            status="success",
            data={"vehicle_id_number": master.vehicle_id_number}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve VIN: {str(e)}"
        )


# get dropdown of masters
@router.get("/masters/dropdown")
def get_masters_dropdown(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    masters = get_all_masters_for_dropdown(db)
    return [{"id": m[0], "vin": m[1], "owner": m[2]} for m in masters]


# create new contact for master record
@router.post(
    "/{master_id}/contacts",
    response_model=ApiResponse[VehicleRegistrationContact],
    summary="Create a new contact for a master record",
)
def create_vehicle_contact(
    master_id: str,
    payload: VehicleRegistrationContactCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = create_contact(db, master_id, payload)

        contact_response = VehicleRegistrationContact.model_validate(result)

        return ApiResponse(
            status="success",
            message=f"Contact created successfully",
            data=contact_response
        )
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contact: {str(e)}"
        )


# get all contacts for a specific master record
@router.get(
    "/{master_id}/contacts",
    response_model=ApiResponse[List[VehicleRegistrationContact]],
    summary="Get all contacts for a master record",
)
def get_vehicle_contacts(
    master_id: str,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):

    try:
        contacts = get_contacts_by_master(db, master_id)

        contacts_response = [
            VehicleRegistrationContact.model_validate(c) for c in contacts
        ]

        return ApiResponse(
            status="success",
            data=contacts_response
        )
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contacts: {str(e)}"
        )


# get single by id
@router.get(
    "/contacts/{contact_id}",
    response_model=ApiResponse[VehicleRegistrationContact],
    summary="Get a single contact by ID",
)
def get_single_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        contact = get_contact(db, contact_id)

        contact_response = VehicleRegistrationContact.model_validate(contact)

        return ApiResponse(
            status="success",
            data=contact_response
        )
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contact: {str(e)}"
        )


# Update
@router.put(
    "/contacts/{contact_id}",
    response_model=ApiResponse[VehicleRegistrationContact],
    summary="Update a contact",
)
def update_vehicle_contact(
    contact_id: int,
    payload: VehicleRegistrationContactCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = update_contact(db, contact_id, payload)

        contact_response = VehicleRegistrationContact.model_validate(result)
        
        return ApiResponse(
            status="success",
            message=f"Contact {contact_id} updated successfully",
            data=contact_response
        )
    
    except HTTPException as e:
        # Contact not found
        raise e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update contact: {str(e)}"
        )

# delete
@router.delete(
    "/contacts/{contact_id}",
    response_model=ApiResponse,
    summary="Delete a contact",
)
def delete_vehicle_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    #current_user: user_models.User = Depends(get_current_user)
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:

        result = delete_contact(db, contact_id)    

        return ApiResponse(
            status="success",
            message=f"Contact deleted successfully",
            data=result
        )
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete contact: {str(e)}"
        )


# get al
@router.get(
    "/contacts",
    response_model=ApiResponse[List[VehicleRegistrationContact]],
    summary="Get all contacts (paginated)",
)
def list_all_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
    permission_check = Depends(PermissionChecker("vr:view_list")),
):
    try:

        contacts = get_all_contacts(db, skip=skip, limit=limit)

        contacts_response = [
            VehicleRegistrationContact.model_validate(c) for c in contacts
        ]
        
        return ApiResponse(
            status="success",
            data=contacts_response
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contacts: {str(e)}"
        )


# reciprocal issued uc
@router.post(
    "/reciprocal-issued",
    response_model=ApiResponse[VehicleRegistrationReciprocalIssued],
)
def create_ri(
    payload: VehicleRegistrationReciprocalIssuedCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = create_reciprocal_issued(db, payload)
        data = VehicleRegistrationReciprocalIssued.model_validate(result)
        return ApiResponse(
            status="success",
            message="Reciprocal Issued created successfully",
            data=data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Reciprocal Issued: {str(e)}"
        )


@router.get(
    "/{master_id}/reciprocal-issued",
    response_model=ApiResponse[List[VehicleRegistrationReciprocalIssued]],
)
def list_ri_for_master(
    master_id: str,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        reciprocals = get_reciprocal_issued_by_master(db, master_id)
        data = [VehicleRegistrationReciprocalIssued.model_validate(r) for r in reciprocals]
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Reciprocal Issued: {str(e)}"
        )


@router.get(
    "/reciprocal-issued/{reciprocal_id}",
    response_model=ApiResponse[VehicleRegistrationReciprocalIssued],
)
def get_ri(
    reciprocal_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        reciprocal = get_reciprocal_issued_by_id(db, reciprocal_id)
        data = VehicleRegistrationReciprocalIssued.model_validate(reciprocal)
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Reciprocal Issued: {str(e)}"
        )


@router.put(
    "/reciprocal-issued/{reciprocal_id}",
    response_model=ApiResponse[VehicleRegistrationReciprocalIssued],
)
def update_ri(
    reciprocal_id: int,
    payload: VehicleRegistrationReciprocalIssuedCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = update_reciprocal_issued(db, reciprocal_id, payload)
        data = VehicleRegistrationReciprocalIssued.model_validate(result)
        return ApiResponse(status="success", message="Reciprocal Issued updated successfully", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Reciprocal Issued: {str(e)}"
        )


@router.delete(
    "/reciprocal-issued/{reciprocal_id}",
    response_model=ApiResponse,
)
def delete_ri(
    reciprocal_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = delete_reciprocal_issued(db, reciprocal_id)
        return ApiResponse(status="success", message=result["message"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Reciprocal Issued: {str(e)}"
        )

# get all
@router.get(
    "/reciprocal-issued",
    response_model=ApiResponse[List[VehicleRegistrationReciprocalIssued]],
)
def list_all_ri(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_list")),
):
    try:
        reciprocals = get_all_reciprocal_issued(db, skip=skip, limit=limit)
        data = [VehicleRegistrationReciprocalIssued.model_validate(r) for r in reciprocals]
        return ApiResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Reciprocal Issued: {str(e)}"
        )


# reciprocal received

@router.post(
    "/reciprocal-received",
    response_model=ApiResponse[VehicleRegistrationReciprocalReceived]
)
def create_rr(
    payload: VehicleRegistrationReciprocalReceivedCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = create_reciprocal_received(db, payload)
        data = VehicleRegistrationReciprocalReceived.model_validate(result)
        return ApiResponse(
            status="success",
            message="Reciprocal Received created successfully",
            data=data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Reciprocal Received: {str(e)}"
        )


@router.get(
    "/{master_id}/reciprocal-received",
    response_model=ApiResponse[List[VehicleRegistrationReciprocalReceived]]
)
def list_rr_for_master(
    master_id: str,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        reciprocals = get_reciprocal_received_by_master(db, master_id)
        data = [VehicleRegistrationReciprocalReceived.model_validate(r) for r in reciprocals]
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Reciprocal Received: {str(e)}"
        )


@router.get(
    "/reciprocal-received/{reciprocal_id}",
    response_model=ApiResponse[VehicleRegistrationReciprocalReceived]
)
def get_rr(
    reciprocal_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        reciprocal = get_reciprocal_received(db, reciprocal_id)
        data = VehicleRegistrationReciprocalReceived.model_validate(reciprocal)
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Reciprocal Received: {str(e)}"
        )


@router.put(
    "/reciprocal-received/{reciprocal_id}",
    response_model=ApiResponse[VehicleRegistrationReciprocalReceived]
)
def update_rr(
    reciprocal_id: int,
    payload: VehicleRegistrationReciprocalReceivedCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = update_reciprocal_received(db, reciprocal_id, payload)
        data = VehicleRegistrationReciprocalReceived.model_validate(result)
        return ApiResponse(status="success", message="Reciprocal Received updated successfully", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Reciprocal Received: {str(e)}"
        )


@router.delete(
    "/reciprocal-received/{reciprocal_id}",
    response_model=ApiResponse
)
def delete_rr(
    reciprocal_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = delete_reciprocal_received(db, reciprocal_id)
        return ApiResponse(status="success", message=result["message"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Reciprocal Received: {str(e)}"
        )

# get all
@router.get(
    "/reciprocal-received",
    response_model=ApiResponse[List[VehicleRegistrationReciprocalReceived]]
)
def list_all_rr(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_list")),
):
    try:
        reciprocals = get_all_reciprocal_received(db, skip=skip, limit=limit)
        data = [VehicleRegistrationReciprocalReceived.model_validate(r) for r in reciprocals]
        return ApiResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Reciprocal Received: {str(e)}"
        )


# trap info uc

@router.post(
    "/undercover/{undercover_id}/trap-info",
    response_model=ApiResponse[VehicleRegistrationUnderCoverTrapInfo]
)
def create_ti_uc(
    undercover_id: int,
    payload: VehicleRegistrationUnderCoverTrapInfoCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = create_trap_info_undercover(db, undercover_id, payload)
        data = VehicleRegistrationUnderCoverTrapInfo.model_validate(result)
        return ApiResponse(
            status="success",
            message="Trap Info (UC) created successfully",
            data=data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Trap Info (UC): {str(e)}"
        )


@router.get(
    "/undercover/{undercover_id}/trap-info",
    response_model=ApiResponse[List[VehicleRegistrationUnderCoverTrapInfo]]
)
def list_ti_uc_for_undercover(
    undercover_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        trap_infos = get_trap_info_undercover_by_uc(db, undercover_id)
        data = [VehicleRegistrationUnderCoverTrapInfo.model_validate(t) for t in trap_infos]
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Trap Info (UC): {str(e)}"
        )


@router.get(
    "/trap-info-uc/{trap_info_id}",
    response_model=ApiResponse[VehicleRegistrationUnderCoverTrapInfo]
)
def get_ti_uc(
    trap_info_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        trap_info = get_trap_info_undercover(db, trap_info_id)
        data = VehicleRegistrationUnderCoverTrapInfo.model_validate(trap_info)
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Trap Info (UC): {str(e)}"
        )


@router.put(
    "/trap-info-uc/{trap_info_id}",
    response_model=ApiResponse[VehicleRegistrationUnderCoverTrapInfo]
)
def update_ti_uc(
    trap_info_id: int,
    payload: VehicleRegistrationUnderCoverTrapInfoCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = update_trap_info_undercover(db, trap_info_id, payload)
        data = VehicleRegistrationUnderCoverTrapInfo.model_validate(result)
        return ApiResponse(status="success", message="Trap Info (UC) updated successfully", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Trap Info (UC): {str(e)}"
        )


@router.delete(
    "/trap-info-uc/{trap_info_id}",
    response_model=ApiResponse
)
def delete_ti_uc(
    trap_info_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = delete_trap_info_undercover(db, trap_info_id)
        return ApiResponse(status="success", message=result["message"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Trap Info (UC): {str(e)}"
        )

# get all
@router.get(
    "/trap-info-uc",
    response_model=ApiResponse[List[VehicleRegistrationUnderCoverTrapInfo]]
)
def list_all_ti_uc(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor/Manager", "Supervisor / Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_list")),
):
    try:
        trap_infos = get_all_trap_info_undercover(db, skip=skip, limit=limit)
        data = [VehicleRegistrationUnderCoverTrapInfo.model_validate(t) for t in trap_infos]
        return ApiResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Trap Info (UC): {str(e)}"
        )


# trap info fictitious routes

@router.post(
    "/fictitious/{fictitious_id}/trap-info",
    response_model=ApiResponse[VehicleRegistrationFictitiousTrapInfo]
)
def create_ti_fc(
    fictitious_id: int,
    payload: VehicleRegistrationFictitiousTrapInfoCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = create_trap_info_fictitious(db, fictitious_id, payload)
        data = VehicleRegistrationFictitiousTrapInfo.model_validate(result)
        return ApiResponse(
            status="success",
            message="Trap Info (FC) created successfully",
            data=data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Trap Info (FC): {str(e)}"
        )


@router.get(
    "/fictitious/{fictitious_id}/trap-info",
    response_model=ApiResponse[List[VehicleRegistrationFictitiousTrapInfo]]
)
def list_ti_fc_for_fictitious(
    fictitious_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        trap_infos = get_trap_info_fictitious_by_fc(db, fictitious_id)
        data = [VehicleRegistrationFictitiousTrapInfo.model_validate(t) for t in trap_infos]
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Trap Info (FC): {str(e)}"
        )


@router.get(
    "/trap-info-fc/{trap_info_id}",
    response_model=ApiResponse[VehicleRegistrationFictitiousTrapInfo]
)
def get_ti_fc(
    trap_info_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_details")),
):
    try:
        trap_info = get_trap_info_fictitious(db, trap_info_id)
        data = VehicleRegistrationFictitiousTrapInfo.model_validate(trap_info)
        return ApiResponse(status="success", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Trap Info (FC): {str(e)}"
        )


@router.put(
    "/trap-info-fc/{trap_info_id}",
    response_model=ApiResponse[VehicleRegistrationFictitiousTrapInfo]
)
def update_ti_fc(
    trap_info_id: int,
    payload: VehicleRegistrationFictitiousTrapInfoCreateBody,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = update_trap_info_fictitious(db, trap_info_id, payload)
        data = VehicleRegistrationFictitiousTrapInfo.model_validate(result)
        return ApiResponse(status="success", message="Trap Info (FC) updated successfully", data=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Trap Info (FC): {str(e)}"
        )


@router.delete(
    "/trap-info-fc/{trap_info_id}",
    response_model=ApiResponse
)
def delete_ti_fc(
    trap_info_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("vr:edit")),
):
    try:
        result = delete_trap_info_fictitious(db, trap_info_id)
        return ApiResponse(status="success", message=result["message"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Trap Info (FC): {str(e)}"
        )

# get all
@router.get(
    "/trap-info-fc",
    response_model=ApiResponse[List[VehicleRegistrationFictitiousTrapInfo]]
)
def list_all_ti_fc(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "Manager", "User")),
    permission_check = Depends(PermissionChecker("vr:view_list")),
):
    try:
        trap_infos = get_all_trap_info_fictitious(db, skip=skip, limit=limit)
        data = [VehicleRegistrationFictitiousTrapInfo.model_validate(t) for t in trap_infos]
        return ApiResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Trap Info (FC): {str(e)}"
        )
