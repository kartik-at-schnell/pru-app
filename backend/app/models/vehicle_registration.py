from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from .base import BaseModel

# main vehicle registration table - stores all extracted data
class VehicleRegistrationMaster(BaseModel):
    __tablename__ = "vehicle_registration_master"
    
    id = Column(String(17), primary_key=True, index=True, nullable=False)
    license_number = Column(String(20), unique=True, index=True)
    vehicle_id_number = Column(String(20), index=True)
    registered_owner = Column(String(200))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50), default="California")
    zip_code = Column(String(10))
    
    #vehicle info
    make = Column(String(50))
    model = Column(String(100))
    year_model = Column(Integer)
    body_type = Column(String(50))
    type_license = Column(String(50))
    type_vehicle = Column(String(50))
    category = Column(String(50))
    
    # registration info
    expiration_date = Column(Date)
    date_issued = Column(Date)
    date_fee_received = Column(Date)
    amount_paid = Column(Numeric(10, 2)) # Decimal for money
    use_tax = Column(Numeric(10, 2))
    sticker_issued = Column(String(50))
    sticker_numbers = Column(String(100))
    
    # system fields
    approval_status = Column(String(20), default="pending") # pending, approved, rejected
    active_status = Column(Boolean, default=True)
    record_type = Column(String(20), default="master") # master, undercover, fictitious
    description = Column(Text)
    error_text = Column(Text)
    
    # relationships with child tables
    undercover_records = relationship("VehicleRegistrationUnderCover", back_populates="master_record")
    fictitious_records = relationship("VehicleRegistrationFictitious", back_populates="master_record")
    contacts = relationship("VehicleRegistrationContact", back_populates="master_record")
    reciprocal_issued = relationship("VehicleRegistrationReciprocalIssued", back_populates="master_record")
    reciprocal_received = relationship("VehicleRegistrationReciprocalReceived", back_populates="master_record")

# undercover/confidential vehicle registrations
class VehicleRegistrationUnderCover(BaseModel):
    __tablename__ = "vehicle_registration_undercover"
    
    id = Column(Integer, primary_key=True, index=True)
    master_record_id = Column(String(17), ForeignKey("vehicle_registration_master.id")) # linking to master table
    license_number = Column(String(20), unique=True, index=True, nullable=True)
    vehicle_id_number = Column(String(17), index=True)
    registered_owner = Column(String(200), nullable=False)
    
    # address information
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50), default="California")
    zip_code = Column(String(10))
    
    # vehicle information
    make = Column(String(50))
    year_model = Column(Integer)
    class_type = Column(String(50))
    type_license = Column(String(50))
    
    # reg info
    expiration_date = Column(Date)
    date_issued = Column(Date)
    date_fee_received = Column(Date)
    amount_paid = Column(Numeric(10, 2))
    
    # system info
    approval_status = Column(String(20), default="pending")
    active_status = Column(Boolean, default=True)
    error_text = Column(Text)
    
    # relationships
    master_record = relationship("VehicleRegistrationMaster", back_populates="undercover_records")
    trap_info = relationship("VehicleRegistrationUnderCoverTrapInfo", back_populates="undercover_record")

# fake/placeholder registrations for verification/testing
class VehicleRegistrationFictitious(BaseModel):
    __tablename__ = "vehicle_registration_fictitious"
    
    id = Column(Integer, primary_key=True, index=True)
    # link to master record
    master_record_id = Column(String(17), ForeignKey("vehicle_registration_master.id"))
    license_number = Column(String(20), index=True, nullable=False)
    vehicle_id_number = Column(String(17), index=True)
    registered_owner = Column(String(200), nullable=False)
    
    # address info
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50), default="California")
    zip_code = Column(String(10))
    
    # vehicle info
    make = Column(String(50))
    model = Column(String(100))
    year_model = Column(Integer)
    vlp_class = Column(String(50))
    
    # financial
    amount_due = Column(Numeric(10, 2))
    amount_received = Column(Numeric(10, 2))
    
    # sys info
    approval_status = Column(String(20), default="pending")
    active_status = Column(Boolean, default=True)
    error_text = Column(Text)
    
    # relations
    master_record = relationship("VehicleRegistrationMaster", back_populates="fictitious_records")
    trap_info = relationship("VehicleRegistrationFictitiousTrapInfo", back_populates="fictitious_record")

#other tables

# undercover tables metadata
class VehicleRegistrationUnderCoverTrapInfo(BaseModel):
    __tablename__ = "vehicle_registration_undercover_trap_info"
    
    id = Column(Integer, primary_key=True, index=True)
    undercover_id = Column(Integer, ForeignKey("vehicle_registration_undercover.id"))
    date = Column(Date)
    number = Column(String(100))
    
    # relation
    undercover_record = relationship("VehicleRegistrationUnderCover", back_populates="trap_info")

#contact information linked to vehicle records
class VehicleRegistrationContact(BaseModel):
    __tablename__ = "vehicle_registration_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    master_record_id = Column(String(17), ForeignKey("vehicle_registration_master.id"))
    contact_name = Column(String(200))
    department = Column(String(100))
    email = Column(String(100))
    phone_number = Column(String(20))
    alt_contact_1 = Column(String(200))
    alt_contact_2 = Column(String(200))
    
    # relation
    master_record = relationship("VehicleRegistrationMaster", back_populates="contacts")

# recieved reciprocal args
class VehicleRegistrationReciprocalReceived(BaseModel):
    __tablename__ = "vehicle_registration_reciprocal_received"
    
    id = Column(Integer, primary_key=True, index=True)
    master_record_id = Column(String(17), ForeignKey("vehicle_registration_master.id"))
    description = Column(Text)
    license_plate = Column(String(20))
    state = Column(String(50))
    year_of_renewal = Column(Integer)
    cancellation_date = Column(Date)
    sticker_number = Column(String(50))
    
    #relation
    master_record = relationship("VehicleRegistrationMaster", back_populates="reciprocal_received")

class VehicleRegistrationFictitiousTrapInfo(BaseModel):
    __tablename__ = "vehicle_registration_fictitious_trap_info"
    
    id = Column(Integer, primary_key=True, index=True)
    fictitious_id = Column(Integer, ForeignKey("vehicle_registration_fictitious.id"))
    date = Column(Date)
    number = Column(String(100))
    
    fictitious_record = relationship("VehicleRegistrationFictitious", back_populates="trap_info")

class VehicleRegistrationReciprocalIssued(BaseModel):
    __tablename__ = "vehicle_registration_reciprocal_issued"
    
    id = Column(Integer, primary_key=True, index=True)
    master_record_id = Column(String(17), ForeignKey("vehicle_registration_master.id"))
    description = Column(Text)
    license_plate = Column(String(20))
    state = Column(String(50))
    year_of_renewal = Column(Integer)
    cancellation_date = Column(Date)
    sticker_number = Column(String(50))
    
    master_record = relationship("VehicleRegistrationMaster", back_populates="reciprocal_issued")
