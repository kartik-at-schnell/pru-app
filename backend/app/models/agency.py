# app/models/agency.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel


class Agency(BaseModel):
    __tablename__ = "agency"

    id = Column(Integer, primary_key=True, index=True)
    agency_name = Column(String(100), nullable=False, unique=True, index=True)
    agency_code = Column(String(50), nullable=True, unique=True, index=True)
    agency_type_id = Column(Integer, ForeignKey("agency_type.id"), nullable=False, index=True)
    #order_value = Column(Integer, nullable=False, default=0, index=True)
    status = Column(String(20), nullable=False, default="Active")
    #description = Column(Text, nullable=True)
    #contact_email = Column(String(100), nullable=True)
    #contact_phone = Column(String(20), nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_by = Column(String(100))
    modified_at = Column(DateTime, onupdate=func.now(), nullable=True)


    # relationships
    agency_type = relationship("AgencyType", back_populates="agencies")
    orders = relationship("AgencyOrder", back_populates="agency", cascade="all, delete-orphan")


class AgencyType(BaseModel):
    __tablename__ = "agency_type"

    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(50), nullable=False, unique=True, index=True)
    type_description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="Active")
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_by = Column(String(100))
    modified_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # relationship
    agencies = relationship("Agency", back_populates="agency_type")



class AgencyOrder(BaseModel):
    __tablename__ = "agency_order"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agency.id"), nullable=False, index=True)
    display_context = Column(String(50), nullable=False)  # e.g., Dropdown, Report, UI
    order_sequence = Column(Integer, nullable=False)
    is_default = Column(Boolean, nullable=True, default=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_by = Column(String(100))
    modified_at = Column(DateTime, onupdate=func.now(), nullable=True)

    agency = relationship("Agency", back_populates="orders")

    __table_args__ = (
        UniqueConstraint("agency_id", "display_context", name="uq_agency_context"),
    )
