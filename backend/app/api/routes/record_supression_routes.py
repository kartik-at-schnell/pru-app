from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.crud import record_suppression as crud
from app.schemas import record_suppression_schema as schemas

router = APIRouter(
    prefix="/record-suppression",
    tags=["Record Suppression"]
)


# master

@router.post("/", response_model=schemas.RecordSuppressionDetailedResponse)
def create_suppression(
    suppression: schemas.RecordSuppressionCreate,
    db: Session = Depends(get_db)
):
    db_suppression = crud.create_suppression(db, suppression)
    return db_suppression


@router.get("/{suppression_id}", response_model=schemas.RecordSuppressionDetailedResponse)
def get_suppression_detail(
    suppression_id: int,
    db: Session = Depends(get_db)
):
    db_suppression = crud.get_suppression(db, suppression_id)
    if not db_suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")
    return db_suppression


@router.get("/", response_model=List[schemas.RecordSuppressionResponse])
def list_suppressions(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    record_type: Optional[str] = Query(None, description="vr_master, dl_original, etc."),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    suppressions = crud.get_all_suppressions(
        db,
        skip=skip,
        limit=limit,
        record_type=record_type,
        is_active_only=active_only
    )
    return suppressions


@router.get("/check/{record_type}/{record_id}", response_model=dict)
def check_suppression_status(
    record_type: str,
    record_id: int,
    db: Session = Depends(get_db)
):
    is_suppressed = crud.check_if_record_suppressed(db, record_type, record_id)
    suppressions = crud.get_suppressions_by_record(db, record_type, record_id)
    
    return {
        "is_suppressed": is_suppressed,
        "suppression_ids": [s.id for s in suppressions],
        "record_type": record_type,
        "record_id": record_id
    }


@router.put("/{suppression_id}", response_model=schemas.RecordSuppressionResponse)
def update_suppression(
    suppression_id: int,
    update_data: schemas.RecordSuppressionUpdate,
    db: Session = Depends(get_db)
):
    db_suppression = crud.update_suppression(db, suppression_id, update_data)
    if not db_suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")
    return db_suppression


@router.delete("/{suppression_id}")
def delete_suppression(
    suppression_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_suppression(db, suppression_id)
    if not success:
        raise HTTPException(status_code=404, detail="Suppression not found")
    return {"status": "success", "message": "Suppression deleted"}


# detailed 1

@router.post("/{suppression_id}/access-request", response_model=schemas.SuppressionDetail1Response)
def add_access_request(
    suppression_id: int,
    detail: schemas.SuppressionDetail1Create,
    db: Session = Depends(get_db)
):
    db_suppression = crud.get_suppression(db, suppression_id)
    if not db_suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")
    
    return crud.create_detail1(db, suppression_id, detail)


@router.get("/{suppression_id}/access-requests", response_model=List[schemas.SuppressionDetail1Response])
def get_access_requests(
    suppression_id: int,
    db: Session = Depends(get_db)
):
    db_suppression = crud.get_suppression(db, suppression_id)
    if not db_suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")
    
    return crud.get_all_detail1_for_suppression(db, suppression_id)


@router.delete("/access-request/{detail1_id}")
def delete_access_request(
    detail1_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_detail1(db, detail1_id)
    if not success:
        raise HTTPException(status_code=404, detail="Access request not found")
    return {"status": "success", "message": "Access request deleted"}


# detailed 2

@router.post("/{suppression_id}/alias", response_model=schemas.SuppressionDetail2Response)
def add_identity_alias(
    suppression_id: int,
    detail: schemas.SuppressionDetail2Create,
    db: Session = Depends(get_db)
):
    db_suppression = crud.get_suppression(db, suppression_id)
    if not db_suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")
    
    return crud.create_detail2(db, suppression_id, detail)


@router.get("/{suppression_id}/aliases", response_model=List[schemas.SuppressionDetail2Response])
def get_identity_aliases(
    suppression_id: int,
    db: Session = Depends(get_db)
):
    db_suppression = crud.get_suppression(db, suppression_id)
    if not db_suppression:
        raise HTTPException(status_code=404, detail="Suppression not found")
    
    return crud.get_all_detail2_for_suppression(db, suppression_id)


@router.delete("/alias/{detail2_id}")
def delete_identity_alias(
    detail2_id: int,
    db: Session = Depends(get_db)
):
    success = crud.delete_detail2(db, detail2_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alias not found")
    return {"status": "success", "message": "Alias deleted"}