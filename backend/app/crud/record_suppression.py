from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models.record_suppression import (
    RecordSuppression,
    SuppressionDetail1,
    SuppressionDetail2
)
from app.schemas.record_suppression_schema import (
    RecordSuppressionCreate,
    RecordSuppressionUpdate,
    SuppressionDetail1Create,
    SuppressionDetail2Create
)

# master

def create_suppression(db: Session, suppression: RecordSuppressionCreate) -> RecordSuppression:
    db_suppression = RecordSuppression(
        record_type=suppression.record_type,
        record_id=suppression.record_id,
        reason=suppression.reason,
        reason_description=suppression.reason_description,
        effective_date=suppression.effective_date or datetime.utcnow(),
        expiration_date=suppression.expiration_date,
        created_by=suppression.created_by,
        status="active",
        is_active=1
    )
    db.add(db_suppression)
    db.commit()
    db.refresh(db_suppression)
    return db_suppression


def get_suppression(db: Session, suppression_id: int) -> RecordSuppression:
    return db.query(RecordSuppression).filter(RecordSuppression.id == suppression_id).first()


def get_all_suppressions(
    db: Session,
    skip: int = 0,
    limit: int = 25,
    record_type: str = None,
    is_active_only: bool = True
) -> list:
    query = db.query(RecordSuppression)
    
    if is_active_only:
        query = query.filter(RecordSuppression.is_active == 1)
    
    if record_type:
        query = query.filter(RecordSuppression.record_type == record_type)
    
    return query.offset(skip).limit(limit).all()


def get_suppressions_by_record(
    db: Session,
    record_type: str,
    record_id: int
) -> list:
    return db.query(RecordSuppression).filter(
        and_(
            RecordSuppression.record_type == record_type,
            RecordSuppression.record_id == record_id,
            RecordSuppression.is_active == 1
        )
    ).all()


def check_if_record_suppressed(db: Session, record_type: str, record_id: int) -> bool:
    result = db.query(RecordSuppression).filter(
        and_(
            RecordSuppression.record_type == record_type,
            RecordSuppression.record_id == record_id,
            RecordSuppression.is_active == 1,
            RecordSuppression.status == "active"
        )
    ).first()
    return result is not None


def update_suppression(
    db: Session,
    suppression_id: int,
    update_data: RecordSuppressionUpdate
) -> RecordSuppression:
    db_suppression = get_suppression(db, suppression_id)
    if not db_suppression:
        return None
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_suppression, key, value)
    
    db_suppression.updated_at = datetime.utcnow()
    db.add(db_suppression)
    db.commit()
    db.refresh(db_suppression)
    return db_suppression


def delete_suppression(db: Session, suppression_id: int) -> bool:
    db_suppression = get_suppression(db, suppression_id)
    if not db_suppression:
        return False
    
    db_suppression.is_active = 0
    db_suppression.status = "removed"
    db_suppression.updated_at = datetime.utcnow()
    db.add(db_suppression)
    db.commit()
    return True


#detailed 1

def create_detail1(
    db: Session,
    suppression_id: int,
    detail: SuppressionDetail1Create
) -> SuppressionDetail1:
    db_detail = SuppressionDetail1(
        suppression_id=suppression_id,
        date_requested=detail.date_requested or datetime.utcnow(),
        driver_license_vehicle_plate=detail.driver_license_vehicle_plate,
        person_requesting_access=detail.person_requesting_access,
        reason=detail.reason,
        amount_of_time_open=detail.amount_of_time_open,
        initials=detail.initials
    )
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail


def get_detail1(db: Session, detail1_id: int) -> SuppressionDetail1:
    return db.query(SuppressionDetail1).filter(SuppressionDetail1.id == detail1_id).first()


def get_all_detail1_for_suppression(db: Session, suppression_id: int) -> list:
    return db.query(SuppressionDetail1).filter(
        SuppressionDetail1.suppression_id == suppression_id
    ).all()


def delete_detail1(db: Session, detail1_id: int) -> bool:
    db_detail = get_detail1(db, detail1_id)
    if not db_detail:
        return False
    
    db.delete(db_detail)
    db.commit()
    return True


# detailed 2

def create_detail2(
    db: Session,
    suppression_id: int,
    detail: SuppressionDetail2Create
) -> SuppressionDetail2:
    db_detail = SuppressionDetail2(
        suppression_id=suppression_id,
        old_name=detail.old_name,
        old_driver_license_vehicle_plate=detail.old_driver_license_vehicle_plate
    )
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail


def get_detail2(db: Session, detail2_id: int) -> SuppressionDetail2:
    return db.query(SuppressionDetail2).filter(SuppressionDetail2.id == detail2_id).first()


def get_all_detail2_for_suppression(db: Session, suppression_id: int) -> list:
    return db.query(SuppressionDetail2).filter(
        SuppressionDetail2.suppression_id == suppression_id
    ).all()


def delete_detail2(db: Session, detail2_id: int) -> bool:
    db_detail = get_detail2(db, detail2_id)
    if not db_detail:
        return False
    
    db.delete(db_detail)
    db.commit()
    return True