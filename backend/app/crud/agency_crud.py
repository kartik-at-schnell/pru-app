# app/crud/agency_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException
from typing import List, Optional

from app.models.agency import Agency, AgencyType, AgencyOrder
from app.schemas.agency_schema import (
    AgencyCreate, AgencyUpdate,
    AgencyTypeCreate,
    AgencyOrderCreate
)


# Agency CRUD
def create_agency(db: Session, payload: AgencyCreate) -> Agency:
    # uniqueness
    existing = db.query(Agency).filter(func.lower(Agency.agency_name) == payload.agency_name.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agency with the same name already exists")

    # confirm agency_type exists
    at = db.query(AgencyType).filter(AgencyType.id == payload.agency_type_id).first()
    if not at:
        raise HTTPException(status_code=404, detail="Agency type not found")

    agency = Agency(
        agency_name=payload.agency_name,
        agency_code=payload.agency_code,
        agency_type_id=payload.agency_type_id,
        status=payload.status or "Active",
        created_by=payload.created_by
    )
    db.add(agency)
    db.commit()
    db.refresh(agency)
    return agency

def get_agency(db: Session, agency_id: int) -> Agency:
    a = db.query(Agency).filter(Agency.id == agency_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Agency not found")
    return a

def list_agencies(
    db: Session,
    search: Optional[str] = None,
    agency_type_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Agency]:
    q = db.query(Agency)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Agency.agency_name.ilike(like), Agency.agency_code.ilike(like)))
    if agency_type_id:
        q = q.filter(Agency.agency_type_id == agency_type_id)
    if status:
        q = q.filter(Agency.status == status)
    q = q.order_by(Agency.agency_name.asc())
    return q.offset(skip).limit(limit).all()

def update_agency(db: Session, agency_id: int, payload: AgencyUpdate) -> Agency:
    a = get_agency(db, agency_id)
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if hasattr(a, k):
            setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a

def activate_agency(db: Session, agency_id: int) -> Agency:
    a = get_agency(db, agency_id)
    a.status = "Active"
    db.commit()
    db.refresh(a)
    return a

def deactivate_agency(db: Session, agency_id: int) -> Agency:
    a = get_agency(db, agency_id)
    a.status = "Inactive"
    db.commit()
    db.refresh(a)
    return a

def delete_agency(db: Session, agency_id: int):
    a = get_agency(db, agency_id)
    # optionally ensure no license records reference this agency; we won't delete if references exist
    # NOTE: your DriverLicenseOriginalRecord currently stores `agency` as text; if you migrate to FK later,
    # add a check here to ensure safe deletion.
    db.delete(a)
    db.commit()
    return {"message": f"Agency {agency_id} deleted successfully"}


def create_agency_type(db: Session, payload: AgencyTypeCreate) -> AgencyType:
    # check uniqueness
    existing = db.query(AgencyType).filter(func.lower(AgencyType.type_name) == payload.type_name.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agency type with this name already exists")
    at = AgencyType(
        type_name=payload.type_name,
        type_description=payload.type_description,
        status=payload.status,
        created_by=payload.created_by
    )
    db.add(at)
    db.commit()
    db.refresh(at)
    return at

def list_agency_types(db: Session, skip: int = 0, limit: int = 100) -> List[AgencyType]:
    return db.query(AgencyType).order_by(AgencyType.type_name.asc()).offset(skip).limit(limit).all()

def get_agency_type(db: Session, type_id: int) -> AgencyType:
    at = db.query(AgencyType).filter(AgencyType.id == type_id).first()
    if not at:
        raise HTTPException(status_code=404, detail="Agency type not found")
    return at

def update_agency_type(db: Session, type_id: int, payload: AgencyTypeCreate) -> AgencyType:
    at = get_agency_type(db, type_id)
    at.type_name = payload.type_name
    at.type_description = payload.type_description
    at.status = payload.status
    at.updated_by = payload.created_by
    db.commit()
    db.refresh(at)
    return at

def delete_agency_type(db: Session, type_id: int):
    at = get_agency_type(db, type_id)
    # optionally ensure no agencies exist - conservatively block deletion
    linked = db.query(Agency).filter(Agency.agency_type_id == type_id).first()
    if linked:
        raise HTTPException(status_code=400, detail="Cannot delete agency type while agencies reference it")
    db.delete(at)
    db.commit()
    return {"message": f"Agency type {type_id} deleted successfully"}



# AgencyOrder CRUD
def upsert_agency_order(db: Session, payload: AgencyOrderCreate) -> AgencyOrder:
    # ensure agency exists
    agency = db.query(Agency).filter(Agency.id == payload.agency_id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    existing = db.query(AgencyOrder).filter(
        AgencyOrder.agency_id == payload.agency_id,
        AgencyOrder.display_context == payload.display_context
    ).first()

    if existing:
        existing.order_sequence = payload.order_sequence
        existing.is_default = payload.is_default
        existing.updated_by = payload.created_by
        db.commit()
        db.refresh(existing)
        return existing

    new = AgencyOrder(
        agency_id=payload.agency_id,
        display_context=payload.display_context,
        order_sequence=payload.order_sequence,
        is_default=payload.is_default,
        created_by=payload.created_by
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def get_orders_by_context(db: Session, display_context: str) -> List[AgencyOrder]:
    return db.query(AgencyOrder).filter(AgencyOrder.display_context == display_context).order_by(AgencyOrder.order_sequence.asc()).all()

def delete_agency_order(db: Session, order_id: int):
    order = db.query(AgencyOrder).filter(AgencyOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Agency order not found")
    db.delete(order)
    db.commit()
    return {"message": f"Agency order {order_id} deleted successfully"}
