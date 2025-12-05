from sqlalchemy import Column, DateTime, Integer, String, Time, Boolean, Text, ForeignKey, Numeric, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.database import Base

# base model with common fields for all tables
class BaseModel(Base):
    __abstract__ = True  # wont create table
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

# reference table for all possible actions in the system
class ActionType(Base):
    __tablename__ = "action_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)  # approve, reject, on_hold
    description = Column(Text)
    is_active = Column(Boolean, default=True)

# log all actions performed on any record
class RecordActionLog(Base):
    __tablename__ = "record_action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, nullable=False)
    record_type = Column(String(50), nullable=False)  # vehicle_registration_master, etc
    action_type_id = Column(Integer, ForeignKey("action_types.id"))
    
    user_id = Column(String(100), nullable=False)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    notes = Column(Text, nullable=True)