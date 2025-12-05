from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

# main reord
class DriverLicenseOriginalRecord(BaseModel):
    __tablename__ = "driver_license"

    id = Column(Integer, primary_key=True, index=True)

    active_status = Column(Boolean, default=True)
    tln = Column(String(50)) 
    tfn = Column(String(50)) 
    tdl = Column(String(50)) 
    fln = Column(String(50)) 
    ffn = Column(String(50)) 
    fdl = Column(String(50)) 
    agency = Column(String(100))
    contact = Column(String(100))
    date_issued = Column(Date)
    modified = Column(DateTime(timezone=True))
    approval_status = Column(String(50), default="pending")
    is_suppressed = Column(Boolean, default=False, index=True)

    # relationship
    contacts = relationship("DriverLicenseContact", back_populates="original_record")
    fictitious_traps = relationship("DriverLicenseFictitiousTrap", back_populates="original_record")


# dl contact
class DriverLicenseContact(BaseModel):
    __tablename__ = "driver_license_contact"

    id = Column(Integer, primary_key=True, index=True)
    
    # fk linking to the original record
    original_record_id = Column(Integer, ForeignKey("driver_license.id"), nullable=True)

    content_type_id = Column(String(255))
    title = Column(String(255))
    modified = Column(DateTime(timezone=True))
    created = Column(DateTime(timezone=True))
    author_id = Column(Integer)
    editor_id = Column(Integer)
    odata_ui_version_string = Column(String(50))
    attachments = Column(Boolean)
    guid = Column(String(50))
    compliance_asset_id = Column(String(255))
    
    contact_name = Column(String(200))
    department1 = Column(String(100))
    address = Column(Text)
    email = Column(String(100))
    phone_number = Column(String(50))
    
    alternative_contact1 = Column(String(200)) 
    alternative_contact2 = Column(String(200)) 
    alternative_contact3 = Column(String(200)) 
    alternative_contact4 = Column(String(200)) 
    
    odata_color_tag = Column(String(50))

    is_suppressed = Column(Boolean, default=False, index=True)

    # relations
    original_record = relationship("DriverLicenseOriginalRecord", back_populates="contacts")


# dl fictitious trap table
class DriverLicenseFictitiousTrap(BaseModel):
    __tablename__ = "driver_license_fictitious_trap"

    id = Column(Integer, primary_key=True, index=True)

    #fk
    original_record_id = Column(Integer, ForeignKey("driver_license.id"), nullable=True)
    
    date = Column(Date) 
    number = Column(String(50)) 
    fictitious_id = Column(Integer)
    
    test = Column(String(50))
    title = Column(String(255))
    compliance_asset_id = Column(String(255))
    color_tag = Column(String(50))
    test2 = Column(String(50))
    content_type = Column(String(100))
    
    version = Column(String(50)) 
    attachments = Column(Boolean) 
    type = Column(String(50))
    item_child_count = Column(Integer) 
    folder_child_count = Column(Integer) 
    
    label_setting = Column(String(100)) 
    retention_label = Column(String(100)) 
    retention_label_applied = Column(Date)
    label_applied_by = Column(String(100))
    item_is_record = Column(Boolean) 
    app_created_by = Column(String(100)) 
    app_modified_by = Column(String(100)) 

    original_record = relationship("DriverLicenseOriginalRecord", back_populates="fictitious_traps")
