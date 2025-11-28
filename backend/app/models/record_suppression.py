from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class RecordSuppression(Base):

    __tablename__ = "record_suppression_master"
    
    # Primary
    id = Column(Integer, primary_key=True, index=True)
    
    # optional linking
    record_type = Column(String(50), nullable=True)  # vr_master, dl_original
    record_id = Column(Integer, nullable=True)  # actual record ID (optional)
    reason = Column(String(100), nullable=False)  # court_order, privacy_request
    reason_description = Column(Text, nullable=True)
    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=True) 

    status = Column(String(50), default="active")  # active, expired, removed, etc.
    is_active = Column(Integer, default=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # relationships (one-to-many)
    details_1 = relationship("SuppressionDetail1", back_populates="suppression", cascade="all, delete-orphan")
    details_2 = relationship("SuppressionDetail2", back_populates="suppression", cascade="all, delete-orphan")


class SuppressionDetail1(Base):

    __tablename__ = "suppression_detail_1"
    
    id = Column(Integer, primary_key=True, index=True)
    suppression_id = Column(Integer, ForeignKey("record_suppression_master.id", ondelete="CASCADE"), nullable=False)
    
    # Access request details (from HLD)
    date_requested = Column(DateTime, nullable=False, default=datetime.utcnow)
    driver_license_vehicle_plate = Column(String(100), nullable=True)  # which plate/license
    person_requesting_access = Column(String(200), nullable=False)  # who asked
    reason = Column(Text, nullable=False)  # why
    amount_of_time_open = Column(String(100), nullable=False)  # how long
    initials = Column(String(10), nullable=True)  # approver    
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relationship
    suppression = relationship("RecordSuppression", back_populates="details_1")


class SuppressionDetail2(Base):

    __tablename__ = "suppression_detail_2"
    
    id = Column(Integer, primary_key=True, index=True)
    suppression_id = Column(Integer, ForeignKey("record_suppression_master.id", ondelete="CASCADE"), nullable=False)
    
    # historical aliases (from HLD)
    old_name = Column(String(200), nullable=True)  # previous name/alias
    old_driver_license_vehicle_plate = Column(String(100), nullable=True)  # previous plate/license
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relationship
    suppression = relationship("RecordSuppression", back_populates="details_2")
