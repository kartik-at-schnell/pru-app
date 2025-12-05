from typing import List, Optional
from fastapi import APIRouter, Body, Query, UploadFile, File, Form, Depends, HTTPException, Path
from sqlalchemy import func
from sqlalchemy.orm import Session
import shutil
import os
from uuid import uuid4
from app.database import get_db
from app.models.document_library import DocumentLibrary, DocumentAuditLog
from app.schemas.document_schema import DocumentLibrarySchema, DocumentResponse, DocumentUpdateRequest, DocumentUploadResponse
from datetime import datetime

from app.schemas import document_schema
from app.security import get_current_user
from app.models.user_models import User
from app.schemas.base_schema import ApiResponse

router = APIRouter(prefix="/documents", tags=["Document Library"])

UPLOAD_DIR = "app/static/uploads"

# getall
@router.get("/", response_model=ApiResponse[List[DocumentResponse]])
def get_all_documents(
    # status: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DocumentLibrary)

    # if status:
        # query = query.filter(DocumentLibrary.status == status)
    if document_type:
        query = query.filter(DocumentLibrary.document_type == document_type)

    docs = query.filter(DocumentLibrary.is_archived == False)
    docs = query.order_by(DocumentLibrary.created_at.desc()).all()
    return ApiResponse[List[DocumentResponse]](data=docs)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    master_record_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        filename = f"{uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document_url = f"/static/uploads/{filename}"

        # Create doc record
        doc = DocumentLibrary(
            document_name=file.filename,
            document_type=document_type,
            document_size=round(os.path.getsize(file_path) / 1024, 2),
            document_url=document_url,
            master_record_id=master_record_id,
            created_by=current_user.id,
            created_at=func.now()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # logging upload action
        log = DocumentAuditLog(
            document_id=doc.id,
            action="upload",
            performed_by= current_user.id,
            timestamp=func.now(),
            notes="manual upload"
        )
        db.add(log)
        db.commit()

        return DocumentUploadResponse(
            id=doc.id,
            document_name=doc.document_name,
            document_type=doc.document_type,
            document_url=doc.document_url,
            status=doc.status,
            created_by=doc.created_by
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=List[DocumentLibrarySchema])
def list_documents(
    master_record_id: Optional[int] = Query(None),
    document_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DocumentLibrary)

    if master_record_id:
        query = query.filter(DocumentLibrary.master_record_id == master_record_id)
    if document_type:
        query = query.filter(DocumentLibrary.document_type == document_type)
    if status:
        query = query.filter(DocumentLibrary.status == status)

    return query.order_by(DocumentLibrary.created_at.desc()).all()

@router.get("/{document_id}", response_model=DocumentLibrarySchema)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(DocumentLibrary).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return 

@router.post("/ocr/{document_id}")
def simulate_ocr_processing(
    document_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(DocumentLibrary).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    simulated_ocr = {
        "text": "this is a simulated OCR result for testing",
        "confidence": 98.5,
        "fields": {
            "plate": "ABC123",
            "owner": "Someone Someone",
            "vin": "1HGCM82633A004352"
        }
    }

    doc.ocr_response_json = simulated_ocr
    doc.status = "completed"
    db.add(doc)
    db.commit()
    db.refresh(doc)

    log = DocumentAuditLog(
        document_id=doc.id,
        action="ocr_simulated",
        performed_by=current_user.id,
        timestamp=func.now(),
        notes="OCR simulated response attached"
    )
    db.add(log)
    db.commit()

    return {
        "message": "OCR processing simulated successfully",
        "ocr_data": simulated_ocr
    }

# update docs
@router.put("/{document_id}", response_model=DocumentUploadResponse)
def update_document(
document_id: int,
payload: DocumentUpdateRequest = Body(...),
db: Session = Depends(get_db),
current_user: User = Depends(get_current_user)
):
    doc = db.query(DocumentLibrary).filter(DocumentLibrary.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")


    for key, value in payload.dict(exclude_unset=True).items():
        setattr(doc, key, value)


    doc.modified_by = current_user.id
    doc.modified_at = func.now()
    db.commit()
    db.refresh(doc)


    log = DocumentAuditLog(
    document_id=doc.id,
    action="update",
    performed_by=current_user.id,
    timestamp=func.now(),
    notes="Document metadata updated"
    )
    db.add(log)
    db.commit()


    return DocumentUploadResponse(
    id=doc.id,
    document_name=doc.document_name,
    document_type=doc.document_type,
    document_url=doc.document_url,
    status=doc.status,
    created_by=doc.created_by
    )


@router.delete("/{document_id}")
def archive_document(
document_id: int,
db: Session = Depends(get_db),
current_user: User = Depends(get_current_user)
):
    doc = db.query(DocumentLibrary).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")


    doc.is_archived = True
    doc.modified_by = current_user.id
    doc.modified_at = func.now()
    db.commit()


    log = DocumentAuditLog(
    document_id=doc.id,
    action="archive",
    performed_by=current_user.id,
    timestamp=func.now(),
    notes="Document archived (soft delete)"
    )
    db.add(log)
    db.commit()


    return {"message": f"Document {document_id} archived successfully."}