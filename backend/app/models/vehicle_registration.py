from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from .base import BaseModel

class VehicleRegistrationMaster(BaseModel):
    __tablename__ = "vehicle_registration_master"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    license_number = Column(String(20), unique=True, index=True)
    exempted_license_plate = Column(String(50))
    vehicle_id_number = Column(String(20), index=True)
    registered_owner = Column(String(200))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50), default="California")
    zip_code = Column(String(10))
 
    cls = Column(String(50))
    unladen_wt = Column(String(50))
    # related_undercover
    # related_fictitious
 
    make = Column(String(50))
    model = Column(String(100))
    year_model = Column(Integer)
    year_sold = Column(Integer)
    body_type = Column(String(50))
    type_license = Column(String(50))
    type_vehicle = Column(String(50))
    # vlp_class = Column(String(50))
    category = Column(String(50))
 
    expiration_date = Column(Date)
    date_issued = Column(Date)
    date_received = Column(Date)
    date_fee_received = Column(Date)
    amount_paid = Column(Numeric(10, 2))
    amount_due = Column(Numeric(10, 2))
    amount_received = Column(Numeric(10, 2))
    use_tax = Column(Numeric(10, 2))
    sticker_issued = Column(String(50))
    sticker_numbers = Column(String(100))
 
    approval_status = Column(String(20), default="pending")
    active_status = Column(Boolean, default=True)
    record_type = Column(String(20), default="master", nullable=True)
    description = Column(Text)
    error_text = Column(Text)
    link_to_folder = Column(String(500))    #s3 URI to pdf, i assume
    document_id = Column(Integer)   #document id on s3                      
 
    #advance vehicle specs
    cert_type = Column(String(50))                     #certificate type (CERTSTYPED)
    mp = Column(String(50))                            #hp/mp
    mo = Column(String(50))                            #Model code/MO
    axl = Column(String(50))                           #axles
    wc = Column(String(50))                            #weight class
    cc_alco = Column(String(50))                       #CC/ALCO info
    type_vehicle_use = Column(String(50))
 
    contacts = relationship("VehicleRegistrationContact", back_populates="master_record")
    # reciprocal_issued = relationship("VehicleRegistrationReciprocalIssued", back_populates="master_record")
    # reciprocal_received = relationship("VehicleRegistrationReciprocalReceived", back_populates="master_record")
    undercover_records = relationship("VehicleRegistrationUnderCover", back_populates="master_record", cascade="all, delete-orphan")
    fictitious_records = relationship("VehicleRegistrationFictitious", back_populates="master_record", cascade="all, delete-orphan")
 
 
class VehicleRegistrationUnderCover(BaseModel):
    __tablename__ = "vehicle_registration_undercover"
 
    id = Column(Integer, primary_key=True, index=True)
    #master_record_id = Column(Integer, ForeignKey("vehicle_registration_master.id"), nullable=True)
    master_record_id = Column(Integer, nullable=True)
 
    license_number = Column(String(20), unique=True, index=True, nullable=True)
    vehicle_id_number = Column(String(17), index=True)
    registered_owner = Column(String(200), nullable=False)
 
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50), default="California")
    zip_code = Column(String(10))
 
    make = Column(String(50))
    model = Column(String(100))
    year_model = Column(Integer)
    year_sold = Column(Integer)
    # vlp_class = Column(String(50))
    class_type = Column(String(50))
    type_license = Column(String(50))
    body_type = Column(String(50))
    type_vehicle = Column(String(50))
    category = Column(String(50))
 
    mp = Column(String(50))
    mo = Column(String(50))
    axl = Column(String(50))
    wc = Column(String(50))
    unladen_wt = Column(String(50))
    paper_issue_code = Column(String(50))
    cert_type = Column(String(50))
 
    link_to_folder = Column(Text)
    document_id = Column(String(100))
 
    expiration_date = Column(Date)
    date_issued = Column(Date)
    date_received = Column(Date)
    date_fee_received = Column(Date)
    amount_paid = Column(Numeric(10, 2))
    use_tax = Column(Numeric(10, 2))
    amount_due = Column(Numeric(10, 2))
    amount_received = Column(Numeric(10, 2))
    sticker_issued = Column(String(50))
    sticker_numbers = Column(String(100))
 
    active_status = Column(Boolean, default=True)
    error_text = Column(Text)
    description = Column(Text)
 
    master_record = relationship("VehicleRegistrationMaster", back_populates="undercover_records")
    trap_info = relationship("VehicleRegistrationUnderCoverTrapInfo", back_populates="undercover_record", cascade="all, delete-orphan")
 
 
class VehicleRegistrationFictitious(BaseModel):
    __tablename__ = "vehicle_registration_fictitious"
 
    id = Column(Integer, primary_key=True, index=True)
    # master_record_id = Column(Integer, ForeignKey("vehicle_registration_master.id"), nullable=True)
    master_record_id = Column(Integer, nullable=True)
    license_number = Column(String(20), index=True, nullable=False)
    vehicle_id_number = Column(String(17), index=True)
    registered_owner = Column(String(200), nullable=False)
 
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50), default="California")
    zip_code = Column(String(10))
 
    make = Column(String(50))
    model = Column(String(100))
    year_model = Column(Integer)
    vlp_class = Column(String(50))
    body_type = Column(String(50))
    type_license = Column(String(50))
    type_vehicle = Column(String(50))
    category = Column(String(50))  
 
    year_sold = Column(Integer)
    date_issued = Column(Date)
    expiration_date = Column(Date)
    date_fee_received = Column(Date)    
    amount_paid = Column(Numeric(10, 2))                
    amount_due = Column(Numeric(10, 2))
    amount_received = Column(Numeric(10, 2))
    use_tax = Column(Numeric(10, 2))
    sticker_issued = Column(String(50))
    sticker_numbers = Column(String(100))
 
    mp = Column(String(50))
    mo = Column(String(50))
    axl = Column(String(50))
    wc = Column(String(50))
    unladen_wt = Column(String(50))
    paper_issue_code = Column(String(50))
    cert_type = Column(String(50))
    link_to_folder = Column(Text)
 
    active_status = Column(Boolean, default=True)
    error_text = Column(Text)
    description = Column(Text)                        
 
    master_record = relationship("VehicleRegistrationMaster", back_populates="fictitious_records")
    trap_info = relationship("VehicleRegistrationFictitiousTrapInfo", back_populates="fictitious_record")
 
 
class VehicleRegistrationContact(BaseModel):
    __tablename__ = "vehicle_registration_contacts"
 
    id = Column(Integer, primary_key=True, index=True)
    # master_record_id = Column(Integer, ForeignKey("vehicle_registration_master.id"))
    master_record_id = Column(Integer, nullable=False)
    contact_name = Column(String(200))
    department = Column(String(100))
    email = Column(String(100))
    phone_number = Column(String(20))
    address = Column(Text)
    alt_contact_1 = Column(String(200))
    alt_contact_2 = Column(String(200))
    alt_contact_3 = Column(String(200))
    alt_contact_4 = Column(String(200))
 
    master_record = relationship("VehicleRegistrationMaster", back_populates="contacts")
 
class VehicleRegistrationReciprocalIssued(BaseModel):
    __tablename__ = "vehicle_registration_reciprocal_issued"
 
    id = Column(Integer, primary_key=True, index=True)
    master_record_id = Column(Integer, ForeignKey("vehicle_registration_master.id"))
 
    description = Column(Text)
    license_plate = Column(String(20))
    state = Column(String(50))
    year_of_renewal = Column(Integer)
    cancellation_date = Column(Date)
    sticker_number = Column(String(50))
 
    issuing_authority = Column(String(100))
    issuing_state = Column(String(100))
    recipent_state = Column(String(100))
 
    # master_record = relationship("VehicleRegistrationMaster", back_populates="reciprocal_issued")
 
class VehicleRegistrationReciprocalReceived(BaseModel):
    __tablename__ = "vehicle_registration_reciprocal_received"
 
    id = Column(Integer, primary_key=True, index=True)
    # master_record_id = Column(Integer, ForeignKey("vehicle_registration_master.id"))
 
    registered_owner = Column(String(50))
    owner_address = Column(String(100))
    description = Column(Text)
    license_plate = Column(String(20))
    sticker_number = Column(String(50))
 
    year_of_renewal = Column(Integer)
    cancellation_date = Column(Date)
    recieved_date = Column(Date)
    expiry_date = Column(Date)
 
    issuing_authority = Column(String(100))
    issuing_state = Column(String(100))
    recipent_state = Column(String(100))
 
    # master_record = relationship("VehicleRegistrationMaster", back_populates="reciprocal_received")
 
 
class VehicleRegistrationFictitiousTrapInfo(BaseModel):
    __tablename__ = "vehicle_registration_fictitious_trap_info"
 
    id = Column(Integer, primary_key=True, index=True)
    fictitious_id = Column(Integer, ForeignKey("vehicle_registration_fictitious.id"))
    # fictitious_id =Column(Integer, nullable=False)
    date = Column(Date)
    number = Column(String(100))
    officer = Column(String(100))
    location = Column(String(100))
    reason = Column(String(500))

    fictitious_record = relationship("VehicleRegistrationFictitious", back_populates="trap_info")
 
class VehicleRegistrationUnderCoverTrapInfo(BaseModel):
    __tablename__ = "vehicle_registration_undercover_trap_info"
 
    id = Column(Integer, primary_key=True, index=True)
    undercover_id = Column(Integer, ForeignKey("vehicle_registration_undercover.id"))

    date = Column(Date)
    number = Column(String(100))
    officer = Column(String(100))
    location = Column(String(100))
    details = Column(String(500))
 
    verified_by = Column(String(100))
    verification_date = Column(Date)
 
    undercover_record = relationship("VehicleRegistrationUnderCover", back_populates="trap_info")
 
 
 