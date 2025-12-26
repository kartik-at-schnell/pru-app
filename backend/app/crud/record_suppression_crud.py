from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional

from app.models.record_suppression import RecordSuppressionRequest
from app.schemas.record_suppression_schema import (
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
            detail=f"Record from {record_type} with record {record_id} already suppressed"
        )

    suppression = RecordSuppressionRequest(
        record_type=record_type,
        record_id=record_id,
        reason=payload.reason,
        suppressed_at=datetime.utcnow(),
        status="active",
        revoked_at=None,
        revoke_reason=None,
        owner_name=getattr(payload, 'owner_name', None),
        suppression_justification=getattr(payload, 'suppression_justification', None),
        confidentiality_level=getattr(payload, 'confidentiality_level', None),
        requested_by=getattr(payload, 'requested_by', None),
        requestor_email=getattr(payload, 'requestor_email', None),
        requestor_phone=getattr(payload, 'requestor_phone', None),
        department=getattr(payload, 'department', None),
        assigned_unit=getattr(payload, 'assigned_unit', None),
        created_by=payload.requested_by,
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


# def get_active_suppressions(
#     db: Session,
#     record_type: Optional[str] = None,
#     limit: int = 50,
#     offset: int = 0
# ) -> ActiveSuppressionsListAllResponse:
    
#     query = db.query(RecordSuppressionRequest).filter(
#         RecordSuppressionRequest.status == "active"
#     )
    
#     if record_type:
#         query = query.filter(RecordSuppressionRequest.record_type == record_type)
    
#     total = query.count()
#     entries = query.order_by(
#         RecordSuppressionRequest.suppressed_at.desc()
#     ).offset(offset).limit(limit).all()
    
#     suppressions = []
#     for entry in entries:
#         days_suppressed = (datetime.utcnow() - entry.suppressed_at.replace(tzinfo=None)).days
#         suppressions.append(ActiveSuppressionListResponse(
#             suppression_id=entry.id,
#             record_type=entry.record_type,
#             record_id=entry.record_id,
#             reason=entry.reason,
#             suppressed_at=entry.suppressed_at,
#             days_suppressed=days_suppressed,
#             owner_name=entry.owner_name,
#             confidentiality_level=entry.confidentiality_level,
#             assigned_unit=entry.assigned_unit,
#             status=entry.status
#         ))
    
#     return ActiveSuppressionsListAllResponse(
#         total_active=total,
#         suppressions=suppressions
#     )

def get_active_suppressions(
    db: Session,
    record_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> ActiveSuppressionsListAllResponse:
    query = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.status == "active"
    )
    if record_type:
        query = query.filter(RecordSuppressionRequest.record_type == record_type)

    total = query.count()
    entries = (
        query.order_by(RecordSuppressionRequest.suppressed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    suppressions = []
    for entry in entries:
        days_suppressed = (datetime.utcnow() - entry.suppressed_at.replace(tzinfo=None)).days

        record_obj = _get_record_by_type(db, entry.record_type, entry.record_id)
        if record_obj is not None:
            record_detail = {
                c.name: getattr(record_obj, c.name)
                for c in record_obj.__table__.columns
            }
        else:
            record_detail = None

        suppressions.append(
            ActiveSuppressionListResponse(
                suppression_id=entry.id,
                record_type=entry.record_type,
                record_id=entry.record_id,
                reason=entry.reason,
                suppressed_at=entry.suppressed_at,
                days_suppressed=days_suppressed,
                owner_name=getattr(entry, "owner_name", None),
                confidentiality_level=getattr(entry, "confidentiality_level", None),
                assigned_unit=getattr(entry, "assigned_unit", None),
                status=entry.status,
                record_detail=record_detail,
            )
        )

    return ActiveSuppressionsListAllResponse(
        total_active=total,
        suppressions=suppressions,
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
    payload: MasterCreateRequest 
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
    payload: DriverLicenseCreateRequest
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
    
def submit_suppression_request(
    db: Session,
    record_type: str,
    record_id: int,
    suppression_reason: str,
    requested_by: str,
    **kwargs
) -> RecordSuppressionRequest:

    suppression_req = RecordSuppressionRequest(
        record_type=record_type,
        record_id=record_id,
        reason=suppression_reason,
        status="pending",
        approval_status="pending",
        requested_by=requested_by,
        suppression_reason=suppression_reason,
        suppression_justification=kwargs.get("suppression_justification"),
        confidentiality_level=kwargs.get("confidentiality_level"),
        effective_date=kwargs.get("effective_date"),
        expiry_date=kwargs.get("expiry_date"),
        notes_for_reviewer=kwargs.get("notes_for_reviewer"),
        attachment_files=kwargs.get("attachment_files"),
        requestor_email=kwargs.get("requestor_email"),
        requestor_phone=kwargs.get("requestor_phone"),
        department=kwargs.get("department"),
        assigned_unit=kwargs.get("assigned_unit"),
    )
    
    db.add(suppression_req)
    db.commit()
    db.refresh(suppression_req)
    return suppression_req


def approve_suppression_request(
    db: Session,
    request_id: int,
    approved_by: str,
    comments: Optional[str] = None
) -> RecordSuppressionRequest:

    suppression_req = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.id == request_id
    ).first()
    
    if not suppression_req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if suppression_req.approval_status != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Request is already {suppression_req.approval_status}"
        )

    record = _get_record_by_type(db, suppression_req.record_type, suppression_req.record_id)
    if record and hasattr(record, 'is_suppressed'):
        record.is_suppressed = True

    suppression_req.approval_status = "approved"
    suppression_req.approved_by = approved_by
    suppression_req.approved_at = datetime.utcnow()
    suppression_req.approval_comments = comments
    suppression_req.suppressed_at = datetime.utcnow()
    suppression_req.status = "active"
    
    db.commit()
    db.refresh(suppression_req)
    return suppression_req


def reject_suppression_request(
    db: Session,
    request_id: int,
    rejected_by: str,
    comments: Optional[str] = None
) -> RecordSuppressionRequest:

    suppression_req = db.query(RecordSuppressionRequest).filter(
        RecordSuppressionRequest.id == request_id
    ).first()
    
    if not suppression_req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if suppression_req.approval_status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Request is already {suppression_req.approval_status}"
        )

    suppression_req.approval_status = "rejected"
    suppression_req.approved_by = rejected_by
    suppression_req.approved_at = datetime.utcnow()
    suppression_req.approval_comments = comments
    suppression_req.status = "rejected"
    
    db.commit()
    db.refresh(suppression_req)
    return suppression_req
