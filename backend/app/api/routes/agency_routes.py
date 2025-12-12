from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agency import AgencyOrder
from app.schemas.agency_schema import (
    AgencyCreate, AgencyResponse, AgencyUpdate,
    AgencyTypeCreate, AgencyTypeResponse,
    AgencyOrderCreate, AgencyOrderResponse
)
from app.crud import agency_crud as crud
from app.schemas.base_schema import ApiResponse
from app.models import user_models
from app.security import get_current_user
from app.rbac import RoleChecker, PermissionChecker

router = APIRouter(prefix="/agency", tags=["Agency"])


# Agency endpoints
@router.post("/", response_model=ApiResponse[AgencyResponse])
def create_agency(
    payload: AgencyCreate, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("add_new_agency"))
):
    payload.created_by = getattr(current_user, "id", None)
    agency = crud.create_agency(db, payload)
    return ApiResponse(status="success", message="Agency created successfully", data=agency)

@router.get("/", response_model=ApiResponse[List[AgencyResponse]])
def list_agencies(
    search: Optional[str] = Query(None, description="Search by name or code"),
    agency_type_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "User")),
    permission_check = Depends(PermissionChecker("view_agency_list"))
):
    agencies = crud.list_agencies(db, search=search, agency_type_id=agency_type_id, status=status, skip=skip, limit=limit)
    return ApiResponse(status="success", data=agencies)

@router.get("/details/{agency_id}", response_model=ApiResponse[AgencyResponse])
def get_agency(
    agency_id: int, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "User")),
    permission_check = Depends(PermissionChecker("view_agency_list"))
):
    a = crud.get_agency(db, agency_id)
    return ApiResponse(status="success", data=a)

@router.put("/details/{agency_id}", response_model=ApiResponse[AgencyResponse])
def update_agency(
    agency_id: int, 
    payload: AgencyUpdate, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor")),
    permission_check = Depends(PermissionChecker("edit_agency_details"))
):
    payload.updated_by = getattr(current_user, "id", None)
    updated = crud.update_agency(db, agency_id, payload)
    return ApiResponse(status="success", message=f"Agency {agency_id} updated", data=updated)

@router.post("/details/{agency_id}/activate", response_model=ApiResponse[AgencyResponse])
def activate_agency(
    agency_id: int, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("archive_restore_agency"))
):
    a = crud.activate_agency(db, agency_id)
    return ApiResponse(status="success", message="Agency activated", data=a)

@router.post("/details/{agency_id}/deactivate", response_model=ApiResponse[AgencyResponse])
def deactivate_agency(
    agency_id: int, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("archive_restore_agency"))
):
    a = crud.deactivate_agency(db, agency_id)
    return ApiResponse(status="success", message="Agency deactivated", data=a)

@router.delete("/{agency_id}", response_model=ApiResponse)
def delete_agency(
    agency_id: int, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("delete_agency"))
):
    result = crud.delete_agency(db, agency_id)
    return ApiResponse(status="success", message=result["message"])


# Agency Type endpoints
@router.post("/types", response_model=ApiResponse[AgencyTypeResponse])
def create_type(
    payload: AgencyTypeCreate, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("manage_agency_metadata"))
):
    payload.created_by = getattr(current_user, "id", None)
    at = crud.create_agency_type(db, payload)
    return ApiResponse(status="success", data=at)

@router.get("/types", response_model=ApiResponse[List[AgencyTypeResponse]])
def list_types(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "User")), # Assuming mostly for dropdowns
    permission_check = Depends(PermissionChecker("view_agency_list"))
):
    types = crud.list_agency_types(db, skip=skip, limit=limit)
    return ApiResponse(status="success", data=types)

@router.get("/types/{type_id}", response_model=ApiResponse[AgencyTypeResponse])
def get_type(
    type_id: int, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "User")),
    permission_check = Depends(PermissionChecker("view_agency_list"))
):
    t = crud.get_agency_type(db, type_id)
    return ApiResponse(status="success", data=t)

@router.put("/types/{type_id}", response_model=ApiResponse[AgencyTypeResponse])
def update_type(
    type_id: int, 
    payload: AgencyTypeCreate, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("manage_agency_metadata"))
):
    payload.created_by = getattr(current_user, "id", None)
    updated = crud.update_agency_type(db, type_id, payload)
    return ApiResponse(status="success", data=updated)

@router.delete("/types/{type_id}", response_model=ApiResponse)
def delete_type(
    type_id: int, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("manage_agency_metadata"))
):
    result = crud.delete_agency_type(db, type_id)
    return ApiResponse(status="success", message=result["message"])


# Agency Order endpoints
@router.post("/orders", response_model=ApiResponse[AgencyOrderResponse])
def upsert_order(
    payload: AgencyOrderCreate, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("manage_agency_metadata"))
):
    payload.created_by = getattr(current_user, "id", None)
    order = crud.upsert_agency_order(db, payload)
    return ApiResponse(status="success", data=order)

@router.get("/orders", response_model=ApiResponse[List[AgencyOrderResponse]])
def list_orders(
    display_context: Optional[str] = Query(None), 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(RoleChecker("Admin", "Supervisor", "User")),
    permission_check = Depends(PermissionChecker("view_agency_list"))
):
    if display_context:
        orders = crud.get_orders_by_context(db, display_context)
    else:
        # if no context provided return all orders
        from app.crud.agency_crud import get_orders_by_context as _get
        orders = db.query(AgencyOrder).order_by(AgencyOrder.display_context.asc(), AgencyOrder.order_sequence.asc()).all()
    return ApiResponse(status="success", data=orders)

@router.delete("/orders/{order_id}", response_model=ApiResponse)
def delete_order(
    order_id: int, 
    db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(RoleChecker("Admin")),
    permission_check = Depends(PermissionChecker("manage_agency_metadata"))
):
    result = crud.delete_agency_order(db, order_id)
    return ApiResponse(status="success", message=result["message"])
