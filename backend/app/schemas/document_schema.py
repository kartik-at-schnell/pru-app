from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class DocumentUploadResponse(BaseModel):
    id: int
    document_name: str
    document_type: str
    document_url: str
    status: str
    created_by: Optional[int]

class DocumentLibrarySchema(BaseModel):
    id: int
    document_name: str
    document_type: str
    document_url: str
    status: str
    content_type: str
    created_at: datetime
    created_by: Optional[int]
    modified_by: Optional[int]

    class Config:
        orm_mode = True


class DocumentResponse(BaseModel):
    id: int
    document_name: str
    document_type: str
    document_size: Optional[float]
    document_url: str
    status: str
    content_type: str
    abbyy_batch_id: Optional[str]
    created_at: Optional[datetime]
    master_record_id: Optional[int]
    ocr_response_json: Optional[dict]

    class Config:
        from_attributes = True
