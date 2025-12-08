from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.agency_schema import (
    AgencyCreate, AgencyResponse, AgencyUpdate,
    AgencyTypeCreate, AgencyTypeResponse,
    AgencyOrderCreate, AgencyOrderResponse
)
from app.crud import agency_crud as crud
from app.schemas.base_schema import ApiResponse
from app.models import user_models
from app.security import get_current_user

router = APIRouter(prefix="/agency", tags=["Agency"])


# Agency endpoints
@router.post("/", response_model=ApiResponse[AgencyResponse])
def create_agency(payload: AgencyCreate, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    payload.created_by = getattr(current_user, "id", None)
    created_agency = crud.create_agency(db, payload)
    return ApiResponse(status="success", message="Agency created successfully", data=created_agency)


@router.get("/", response_model=ApiResponse[List[AgencyResponse]])
def list_agencies(
    search: Optional[str] = Query(None, description="Search by name or code"),
    agency_type_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    agencies_list = crud.list_agencies(
        db, search=search, agency_type_id=agency_type_id, status=status
    )
    return ApiResponse(status="success", data=agencies_list)


@router.get("/{agency_id}", response_model=ApiResponse[AgencyResponse])
def get_agency(agency_id: int, db: Session = Depends(get_db)):
    agency_record = crud.get_agency(db, agency_id)
    return ApiResponse(status="success", data=agency_record)


@router.put("/{agency_id}", response_model=ApiResponse[AgencyResponse])
def update_agency(
    agency_id: int,
    payload: AgencyUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    payload.updated_by = getattr(current_user, "id", None)
    updated_agency = crud.update_agency(db, agency_id, payload)
    return ApiResponse(status="success", message=f"Agency {agency_id} updated", data=updated_agency)


@router.post("/{agency_id}/activate", response_model=ApiResponse[AgencyResponse])
def activate_agency(agency_id: int, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    activated_agency = crud.activate_agency(db, agency_id)
    return ApiResponse(status="success", message="Agency activated", data=activated_agency)


@router.post("/{agency_id}/deactivate", response_model=ApiResponse[AgencyResponse])
def deactivate_agency(agency_id: int, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    deactivated_agency = crud.deactivate_agency(db, agency_id)
    return ApiResponse(status="success", message="Agency deactivated", data=deactivated_agency)


@router.delete("/{agency_id}", response_model=ApiResponse)
def delete_agency(agency_id: int, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    delete_result = crud.delete_agency(db, agency_id)
    return ApiResponse(status="success", message=delete_result["message"])


# Agency Type endpoints
@router.post("/types", response_model=ApiResponse[AgencyTypeResponse])
def create_type(payload: AgencyTypeCreate, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    payload.created_by = getattr(current_user, "id", None)
    created_type = crud.create_agency_type(db, payload)
    return ApiResponse(status="success", data=created_type)


@router.get("/types", response_model=ApiResponse[List[AgencyTypeResponse]])
def list_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agency_types = crud.list_agency_types(db, '''skip=skip, limit=limit''')
    return ApiResponse(status="success", data=agency_types)


@router.get("/types/{type_id}", response_model=ApiResponse[AgencyTypeResponse])
def get_type(type_id: int, db: Session = Depends(get_db)):
    agency_type = crud.get_agency_type(db, type_id)
    return ApiResponse(status="success", data=agency_type)


@router.put("/types/{type_id}", response_model=ApiResponse[AgencyTypeResponse])
def update_type(
    type_id: int,
    payload: AgencyTypeCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    payload.created_by = getattr(current_user, "id", None)
    updated_type = crud.update_agency_type(db, type_id, payload)
    return ApiResponse(status="success", data=updated_type)


@router.delete("/types/{type_id}", response_model=ApiResponse)
def delete_type(type_id: int, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    delete_result = crud.delete_agency_type(db, type_id)
    return ApiResponse(status="success", message=delete_result["message"])


# Agency Order endpoints
@router.post("/orders", response_model=ApiResponse[AgencyOrderResponse])
def upsert_order(payload: AgencyOrderCreate, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    payload.created_by = getattr(current_user, "id", None)
    agency_order = crud.upsert_agency_order(db, payload)
    return ApiResponse(status="success", data=agency_order)


@router.get("/orders", response_model=ApiResponse[List[AgencyOrderResponse]])
def list_orders(display_context: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if display_context:
        agency_orders = crud.get_orders_by_context(db, display_context)
    else:
        from app.crud.agency_crud import get_orders_by_context as _get
        agency_orders = db.query(AgencyOrder).order_by(
            AgencyOrder.display_context.asc(),
            AgencyOrder.order_sequence.asc()
        ).all()

    return ApiResponse(status="success", data=agency_orders)


@router.delete("/orders/{order_id}", response_model=ApiResponse)
def delete_order(order_id: int, db: Session = Depends(get_db), current_user: user_models.User = Depends(get_current_user)):
    delete_result = crud.delete_agency_order(db, order_id)
    return ApiResponse(status="success", message=delete_result["message"])
