from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional

from app.models.record_suppression import RecordSuppressionRequest
from app.schemas.record_suppression_schema import (
    CreateSuppressedDLOriginalRequest,
    CreateSuppressedVRMasterRequest,
    SuppressRecordRequest,
    RevokeSuppressionRequest,
    SuppressionHistoryResponse,
    ActiveSuppressionListResponse,
    ActiveSuppressionsListAllResponse,
    RecordSuppressionResponse
)
from app.crud.vehicle_registration_crud import create_master_record
from app.crud.driving_license_crud import create_original_record
from app.schemas.vehicle_registration_schema import MasterCreateRequest
from app.schemas.driving_license_schema import DriverLicenseOriginalCreate as DriverLicenseCreateRequest


def suppress_record(
    db: Session,
    record_type: str,
    record_id: int,
    payload: SuppressRecordRequest
) -> RecordSuppressionRequest:
    
    record = _get_record_by_type(db, record_type, record_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Record {record_type}#{record_id} not found"
        )

    if hasattr(record, 'is_suppressed') and record.is_suppressed:
        raise HTTPException(
            status_code=400,
            detail=f"Record {record_type}#{record_id} already suppressed"
        )

    suppression = RecordSuppressionRequest(
        record_type=record_type,
        record_id=record_id,
        reason=payload.reason,
        suppressed_at=datetime.utcnow(),
        status="active",
        revoked_at=None,
        revoke_reason=None
    )

    db.add(suppression)
    db.flush()

    record.is_suppressed = True
    db.commit()
    db.refresh(suppression)

    return suppression


def revoke_suppression(
    db: Session,
    suppression_id: int,
    payload: RevokeSuppressionRequest
) -> RecordSuppressionRequest:
    
    suppression = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.id == suppression_id
    ).first()

    if not suppression:
        raise HTTPException(
            status_code=404,
            detail=f"Suppression request #{suppression_id} not found"
        )

    if suppression.status == "revoked":
        raise HTTPException(
            status_code=400,
            detail=f"Suppression #{suppression_id} already revoked"
        )

    record = _get_record_by_type(db, suppression.record_type, suppression.record_id)
    if record and hasattr(record, 'is_suppressed'):
        record.is_suppressed = False

    suppression.status = "revoked"
    suppression.revoked_at = datetime.utcnow()
    suppression.revoke_reason = payload.revoke_reason

    db.commit()
    db.refresh(suppression)

    return suppression


def get_suppression_history(
    db: Session,
    record_type: str,
    record_id: int
) -> SuppressionHistoryResponse:
    
    entries = db.query(RecordSuppressionRequest).filter(
        and_(
            RecordSuppressionRequest.record_type == record_type,
            RecordSuppressionRequest.record_id == record_id
        )
    ).order_by(RecordSuppressionRequest.suppressed_at.desc()).all()

    history = [RecordSuppressionResponse.from_orm(entry) for entry in entries]

    return SuppressionHistoryResponse(
        record_type=record_type,
        record_id=record_id,
        total_entries=len(history),
        history=history
    )


def get_active_suppressions(
    db: Session,
    record_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> ActiveSuppressionsListAllResponse:
    
    query = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.status == "active"
    )

    if record_type:
        query = query.filter(RecordSuppressionRequest.record_type == record_type)

    total = query.count()
    entries = query.order_by(
        RecordSuppressionRequest.suppressed_at.desc()
    ).offset(offset).limit(limit).all()

    suppressions = []
    for entry in entries:
        days_suppressed = (datetime.utcnow() - entry.suppressed_at.replace(tzinfo=None)).days
        suppressions.append(ActiveSuppressionListResponse(
            suppression_id=entry.id,
            record_type=entry.record_type,
            record_id=entry.record_id,
            reason=entry.reason,
            suppressed_at=entry.suppressed_at,
            days_suppressed=days_suppressed
        ))

    return ActiveSuppressionsListAllResponse(
        total_active=total,
        suppressions=suppressions
    )


def is_record_suppressed(
    db: Session,
    record_type: str,
    record_id: int
) -> bool:
    
    suppression = db.query(RecordSuppressionRequest).filter(
        and_(
            RecordSuppressionRequest.record_type == record_type,
            RecordSuppressionRequest.record_id == record_id,
            RecordSuppressionRequest.status == "active"
        )
    ).first()

    return suppression is not None


def get_suppression_for_record(
    db: Session,
    record_type: str,
    record_id: int
) -> Optional[RecordSuppressionRequest]:
    
    return db.query(RecordSuppressionRequest).filter(
        and_(
            RecordSuppressionRequest.record_type == record_type,
            RecordSuppressionRequest.record_id == record_id,
            RecordSuppressionRequest.status == "active"
        )
    ).first()


def _get_record_by_type(db: Session, record_type: str, record_id: int):
    
    if record_type == "vr_master":
        from app.models.vehicle_registration import VehicleRegistrationMaster
        return db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.id == record_id
        ).first()
    
    elif record_type == "vr_undercover":
        from app.models.vehicle_registration import VehicleRegistrationUnderCover
        return db.query(VehicleRegistrationUnderCover).filter(
            VehicleRegistrationUnderCover.id == record_id
        ).first()
    
    elif record_type == "vr_fictitious":
        from app.models.vehicle_registration import VehicleRegistrationFictitious
        return db.query(VehicleRegistrationFictitious).filter(
            VehicleRegistrationFictitious.id == record_id
        ).first()
    
    elif record_type == "dl_original":
        from app.models.driving_license import DriverLicenseOriginalRecord
        return db.query(DriverLicenseOriginalRecord).filter(
            DriverLicenseOriginalRecord.id == record_id
        ).first()
    
    return None


def create_suppressed_vr_master(
    db: Session,
    payload: CreateSuppressedVRMasterRequest
):
    
    suppression_reason = payload.suppression_reason
    if not suppression_reason:
        suppression_reason = "Record created in suppressed state"

    master_payload = MasterCreateRequest(
        license_number=payload.license_number,
        vehicle_id_number=payload.vehicle_id_number,
        registered_owner=payload.registered_owner,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        zip_code=payload.zip_code,
        make=payload.make,
        model=payload.model,
        year_model=payload.year_model,
        body_type=payload.body_type,
        type_license=payload.type_license,
        type_vehicle=payload.type_vehicle,
        category=payload.category,
        expiration_date=payload.expiration_date,
        date_issued=payload.date_issued,
        date_received=payload.date_received,
        date_fee_received=payload.date_fee_received,
        amount_paid=payload.amount_paid,
        amount_due=payload.amount_due,
        amount_received=payload.amount_received,
        use_tax=payload.use_tax,
        sticker_issued=payload.sticker_issued,
        sticker_numbers=payload.sticker_numbers,
        cert_type=payload.cert_type,
        mp=payload.mp,
        mo=payload.mo,
        axl=payload.axl,
        wc=payload.wc,
        cc_alco=payload.cc_alco,
        active_status=payload.active_status
    )

    try:
        vr_master = create_master_record(db, master_payload)
        vr_master.is_suppressed = True
        db.flush()

        suppression = RecordSuppressionRequest(
            record_type="vr_master",
            record_id=vr_master.id,
            reason=suppression_reason,
            suppressed_at=datetime.utcnow(),
            status="active",
            revoked_at=None,
            revoke_reason=None
        )

        db.add(suppression)
        db.commit()
        db.refresh(vr_master)
        db.refresh(suppression)

        return {
            "record": vr_master,
            "suppression": suppression
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating suppressed VRMaster: {str(e)}"
        )


def create_suppressed_dl_original(
    db: Session,
    payload: CreateSuppressedDLOriginalRequest
):
    
    suppression_reason = payload.suppression_reason
    if not suppression_reason:
        suppression_reason = "Record created in suppressed state"

    dl_payload = DriverLicenseCreateRequest(
        tln=payload.tln,
        tfn=payload.tfn,
        tdl=payload.tdl,
        fln=payload.fln,
        ffn=payload.ffn,
        fdl=payload.fdl,
        agency=payload.agency,
        contact=payload.contact,
        date_issued=payload.date_issued,
        modified=payload.modified,
        approval_status=payload.approval_status,
        active_status=payload.active_status
    )

    try:
        dl_record = create_original_record(db, dl_payload)
        dl_record.is_suppressed = True
        db.flush()

        suppression = RecordSuppressionRequest(
            record_type="dl_original",
            record_id=dl_record.id,
            reason=suppression_reason,
            suppressed_at=datetime.utcnow(),
            status="active",
            revoked_at=None,
            revoke_reason=None
        )

        db.add(suppression)
        db.commit()
        db.refresh(dl_record)
        db.refresh(suppression)

        return {
            "record": dl_record,
            "suppression": suppression
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating suppressed DriverLicense: {str(e)}"
        )