import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Generator
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:1234567890@localhost:5432/abbyy")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DriverLicense(Base):
    __tablename__ = "driver_licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, index=True)
    document_id = Column(String, unique=True, index=True)
    tn_dl = Column(String)
    fn_dl = Column(String)
    agency = Column(String)
    transcribed_last_name = Column(String)
    transcribed_first_name = Column(String)
    first_last_name = Column(String)
    first_first_name = Column(String)
    date_issued = Column(DateTime)
    expiration_date = Column(DateTime)
    contact = Column(String)
    tracking_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VehicleRegistration(Base):
    __tablename__ = "vehicle_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, index=True)
    document_id = Column(String, unique=True, index=True)
    vin = Column(String, unique=True, index=True)
    license_plate = Column(String, index=True)
    make = Column(String)
    year_model = Column(String)
    year_sold = Column(String)
    body_type = Column(String)
    vehicle_class = Column(String)
    vehicle_type = Column(String)
    type_license = Column(String)
    vehicle_use = Column(String)
    certs_typed = Column(String)
    registered_owner = Column(String)
    date_issued = Column(DateTime)
    expiration_date = Column(DateTime)
    date_received = Column(DateTime)
    pic = Column(String)
    cc_alco = Column(String)
    amount_paid = Column(String)
    lien_holder = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()