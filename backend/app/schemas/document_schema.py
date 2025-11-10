from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class DocumentUploadResponse(BaseModel):
    id: int
    document_name: str
    document_type: str
    document_url: str
    status: str

class DocumentLibrarySchema(BaseModel):
    id: int
    document_name: str
    document_type: str
    document_url: str
    status: str
    content_type: str
    created_at: datetime

    class Config:
        orm_mode = True

