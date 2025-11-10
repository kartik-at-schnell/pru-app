from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class DocumentLibrary(Base):
    __tablename__ = "document_library"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String, nullable=False)
    document_type = Column(String, nullable=False) #vr, dl, suppression
    document_size = Column(Float, nullable=True)
    document_url = Column(String, nullable=False) #s3 path
    status = Column(String, default="pending")
    content_type = Column(String, default="Document")
    abbyy_batch_id = Column(String, nullable=True)
    ocr_response_json = Column(JSON, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    master_record_id = Column(Integer, ForeignKey("vehicle_registration_master.id"), nullable=True)

    #relationship
    master_record = relationship("VehicleRegistrationMaster", backref="documents")

class DocumentAuditLog(Base):
    __tablename__ = "document_audit_log"


    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document_library.id"))
    action = Column(String, nullable=False) # upload, delete, ocr triggered, etc
    performed_by = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=func.now)
    notes = Column(String, nullable=True)


    document = relationship("DocumentLibrary", backref="audit_logs")
