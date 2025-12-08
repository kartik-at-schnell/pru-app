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


#Agency CRUD

def create_agency(db: Session, payload: AgencyCreate) -> Agency:
    existing_agency = db.query(Agency).filter(
        func.lower(Agency.agency_name) == payload.agency_name.lower()
    ).first()

    if existing_agency:
        raise HTTPException(status_code=400, detail="Agency with the same name already exists")

    agency_type = db.query(AgencyType).filter(
        AgencyType.id == payload.agency_type_id
    ).first()

    if not agency_type:
        raise HTTPException(status_code=404, detail="Agency type not found")

    agency = Agency(
        agency_name=payload.agency_name,
        agency_code=payload.agency_code,
        agency_type_id=payload.agency_type_id,
        order_value=payload.order_value or 0,
        status=payload.status or "Active",
        #description=payload.description,
        created_by=payload.created_by
    )

    db.add(agency)
    db.commit()
    db.refresh(agency)
    return agency


def get_agency(db: Session, agency_id: int) -> Agency:
    agency = db.query(Agency).filter(Agency.id == agency_id).first()

    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    return agency


def list_agencies(
    db: Session,
    search: Optional[str] = None,
    agency_type_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Agency]:

    agency_query = db.query(Agency)

    if search:
        like = f"%{search}%"
        agency_query = agency_query.filter(
            or_(
                Agency.agency_name.ilike(like),
                Agency.agency_code.ilike(like)
            )
        )

    if agency_type_id:
        agency_query = agency_query.filter(Agency.agency_type_id == agency_type_id)

    if status:
        agency_query = agency_query.filter(Agency.status == status)

    agency_query = agency_query.order_by(
        Agency.order_value.asc(),
        Agency.agency_name.asc()
    )

    return agency_query.all()


def update_agency(db: Session, agency_id: int, payload: AgencyUpdate) -> Agency:
    agency = get_agency(db, agency_id)

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if hasattr(agency, key):
            setattr(agency, key, value)

    db.commit()
    db.refresh(agency)
    return agency


def activate_agency(db: Session, agency_id: int) -> Agency:
    agency = get_agency(db, agency_id)
    agency.status = "Active"
    db.commit()
    db.refresh(agency)
    return agency


def deactivate_agency(db: Session, agency_id: int) -> Agency:
    agency = get_agency(db, agency_id)
    agency.status = "Inactive"
    db.commit()
    db.refresh(agency)
    return agency


def delete_agency(db: Session, agency_id: int):
    agency = get_agency(db, agency_id)
    db.delete(agency)
    db.commit()
    return {"message": f"Agency {agency_id} deleted successfully"}


#Agency Type CRUD
def create_agency_type(db: Session, payload: AgencyTypeCreate) -> AgencyType:
    existing_type = db.query(AgencyType).filter(
        func.lower(AgencyType.type_name) == payload.type_name.lower()
    ).first()

    if existing_type:
        raise HTTPException(status_code=400, detail="Agency type with this name already exists")

    agency_type = AgencyType(
        type_name=payload.type_name,
        type_description=payload.type_description,
        status=payload.status,
        created_by=payload.created_by
    )

    db.add(agency_type)
    db.commit()
    db.refresh(agency_type)
    return agency_type


def list_agency_types(db: Session) -> List[AgencyType]:
    return db.query(AgencyType).order_by(
        AgencyType.type_name.asc()
    ).all()


def get_agency_type(db: Session, type_id: int) -> AgencyType:
    agency_type = db.query(AgencyType).filter(
        AgencyType.id == type_id
    ).first()

    if not agency_type:
        raise HTTPException(status_code=404, detail="Agency type not found")

    return agency_type


def update_agency_type(db: Session, type_id: int, payload: AgencyTypeCreate) -> AgencyType:
    agency_type = get_agency_type(db, type_id)

    agency_type.type_name = payload.type_name
    agency_type.type_description = payload.type_description
    agency_type.status = payload.status
    agency_type.updated_by = payload.created_by

    db.commit()
    db.refresh(agency_type)
    return agency_type


def delete_agency_type(db: Session, type_id: int):
    agency_type = get_agency_type(db, type_id)

    linked_agency = db.query(Agency).filter(
        Agency.agency_type_id == type_id
    ).first()

    if linked_agency:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete agency type while agencies reference it"
        )

    db.delete(agency_type)
    db.commit()
    return {"message": f"Agency type {type_id} deleted successfully"}


#Agency Order CRUD

def upsert_agency_order(db: Session, payload: AgencyOrderCreate) -> AgencyOrder:
    agency = db.query(Agency).filter(
        Agency.id == payload.agency_id
    ).first()

    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    existing_order = db.query(AgencyOrder).filter(
        AgencyOrder.agency_id == payload.agency_id,
        AgencyOrder.display_context == payload.display_context
    ).first()

    if existing_order:
        existing_order.order_sequence = payload.order_sequence
        existing_order.is_default = payload.is_default
        existing_order.updated_by = payload.created_by
        db.commit()
        db.refresh(existing_order)
        return existing_order

    new_order = AgencyOrder(
        agency_id=payload.agency_id,
        display_context=payload.display_context,
        order_sequence=payload.order_sequence,
        is_default=payload.is_default,
        created_by=payload.created_by
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


def get_orders_by_context(db: Session, display_context: str) -> List[AgencyOrder]:
    return db.query(AgencyOrder).filter(
        AgencyOrder.display_context == display_context
    ).order_by(
        AgencyOrder.order_sequence.asc()
    ).all()


def delete_agency_order(db: Session, order_id: int):
    agency_order = db.query(AgencyOrder).filter(
        AgencyOrder.id == order_id
    ).first()

    if not agency_order:
        raise HTTPException(status_code=404, detail="Agency order not found")

    db.delete(agency_order)
    db.commit()
    return {"message": f"Agency order {order_id} deleted successfully"}
