from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.crud.vehicle_registration_crud import (
    create_vehicle_record,
    get_all_vehicles,
    get_vehicle_by_id,
    update_vehicle_record,
    delete_vehicle_record,
    get_vehicle_master_details
)

from app.schemas.vehicle_registration_schema import(
    VehicleRegistrationMasterCreate,
    VehicleRegistrationMasterBase,
    VehicleRegistrationMaster,
    VehicleRegistrationMasterDetails,
    VehicleRegistrationCreateRequest,
    VehicleRegistrationResponse,
    VehicleRegistrationListItem
)

from app.security import get_current_user
from app.schemas.base_schema import ApiResponse
from app.models import user_models

router = APIRouter(prefix="/vehicle-registration", tags=["Vehicle Registration"])

@router.post("/", response_model=ApiResponse[VehicleRegistrationResponse], status_code=status.HTTP_201_CREATED)
def create_vehicle(
    record: VehicleRegistrationCreateRequest, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(get_current_user)
):
    # Simple wrapper for success
    try:
        new_record = create_vehicle_record(db, record)
        return ApiResponse[VehicleRegistrationResponse](
            status="success",
            message=f"Record created successfully in {record.record_type} table",
            data={
                "id": new_record.id,
                "license_number": new_record.license_number,
                "vehicle_id_number": new_record.vehicle_id_number,
                "registered_owner": new_record.registered_owner,
                "make": new_record.make,
                "model": new_record.model,
                "year_model": new_record.year_model,
                "approval_status": new_record.approval_status,
                "created_at": new_record.created_at,
                "updated_at": new_record.updated_at,
                "record_type": record.record_type
            }
        )
    except ValueError as e:  # Specific error handling for validation
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:  # Basic error catch
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create record: {str(e)}")

@router.get("/", response_model=ApiResponse[List[VehicleRegistrationResponse]])
def list_vehicles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by license number or VIN"),
    record_type: Optional[str] = Query(None, description="Filter by table: master, undercover, fictitious, or null for all"),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    try:
        vehicle_list = get_all_vehicles(db, skip=skip, limit=limit, record_type=record_type, search=search)
        
        # Format response with record_type indicator
        formatted_data = []
        for vehicle in vehicle_list:
            # Determine which table it came from (simple heuristic)
            table_type = "master"  # default
            
            formatted_data.append({
                "id": vehicle.id,
                "license_number": vehicle.license_number,
                "vehicle_id_number": vehicle.vehicle_id_number,
                "registered_owner": vehicle.registered_owner,
                "make": getattr(vehicle, 'make', None),
                "model": getattr(vehicle, 'model', None),
                "year_model": getattr(vehicle, 'year_model', None),
                "approval_status": vehicle.approval_status,
                "created_at": vehicle.created_at,
                "updated_at": vehicle.updated_at,
                "record_type": table_type
            })
        
        return ApiResponse[List[VehicleRegistrationResponse]](
            status="success",
            message=f"Retrieved {len(formatted_data)} records",
            data=formatted_data
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve records: {str(e)}")

# ============================================================================
# READ ONE ROUTE - SEARCHES ALL TABLES
# ============================================================================

@router.get("/{record_id}", response_model=ApiResponse[VehicleRegistrationResponse])
def get_vehicle(
    record_id: str, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(get_current_user)
):
    """
    Get a specific vehicle record by ID (searches all tables: master, undercover, fictitious)
    """
    record = get_vehicle_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Vehicle record not found in any table")
    
    return ApiResponse[VehicleRegistrationResponse](
        status="success",
        data={
            "id": record.id,
            "license_number": record.license_number,
            "vehicle_id_number": record.vehicle_id_number,
            "registered_owner": record.registered_owner,
            "make": getattr(record, 'make', None),
            "model": getattr(record, 'model', None),
            "year_model": getattr(record, 'year_model', None),
            "approval_status": record.approval_status,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "record_type": "master"  # placeholder, can be enhanced to detect
        }
    )

# ============================================================================
# UPDATE ROUTE - SEARCHES ALL TABLES
# ============================================================================

@router.put("/{record_id}", response_model=ApiResponse[VehicleRegistrationResponse])
def update_vehicle(
    record_id: str, 
    update_data: VehicleRegistrationMasterBase, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(get_current_user)
):
    """
    Update a vehicle record (searches all tables)
    """
    updated = update_vehicle_record(db, record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    
    return ApiResponse[VehicleRegistrationResponse](
        status="success",
        message="Record updated successfully",
        data={
            "id": updated.id,
            "license_number": updated.license_number,
            "vehicle_id_number": updated.vehicle_id_number,
            "registered_owner": updated.registered_owner,
            "make": getattr(updated, 'make', None),
            "model": getattr(updated, 'model', None),
            "year_model": getattr(updated, 'year_model', None),
            "approval_status": updated.approval_status,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at,
            "record_type": "master"
        }
    )

# ============================================================================
# DELETE ROUTE - SEARCHES ALL TABLES
# ============================================================================

# delete - searches across all tables
@router.delete("/{record_id}", response_model=ApiResponse)
def delete_vehicle(
    record_id: str, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(get_current_user)
):
    """
    Delete a vehicle record (searches all tables)
    """
    deleted = delete_vehicle_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle record not found")
    
    return ApiResponse(
        status="success",
        message=f"Record ID {record_id} deleted successfully"
    )

# ============================================================================
# DETAILS ENDPOINT - MASTER TABLE ONLY
# ============================================================================

# Details endpoint - for master table with all relationships
@router.get("/{master_id}/details", response_model=ApiResponse[VehicleRegistrationMasterDetails])
def get_master_record_details(
    master_id: str, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(get_current_user)
):
    """
    Get complete details for a master vehicle record with all related data
    (contacts, reciprocal issued/received, undercover records, fictitious records)
    """
    db_record = get_vehicle_master_details(db=db, master_id=master_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Vehicle Master Record not found")
    
    return ApiResponse[VehicleRegistrationMasterDetails](
        status="success",
        data=db_record
    )
