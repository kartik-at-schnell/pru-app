from sqlalchemy import Column, DateTime, Integer, String, Time, Boolean, Text, ForeignKey, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# base model with common fields for all tables
class BaseModel(Base):
    __abstract__ = True #wont create tabkle

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# reference table for all possible actions in the system
class ActionType(Base):
    __table_name__ = "action_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)  # approve, reject, processing, reprocess
    description = Column(Text)
    is_active = Column(Boolean, default=True)

# log all actions performed on any record
class RecordActionLog(Base):
    __table_name__ = "record_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    record_table = Column(String(50), nullable=False)
    action_type_id = Column(Integer, ForeignKey("action_types.id"))
    user_id = Column(Integer, nullable=True)
    notes= Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address= Column(String(50))
    
    action_type = relationship("ActionType", back_populates="action_logs")  #relationship

ActionType.action_logs = relationship("RecordActionLog", back_populates="action_type")
