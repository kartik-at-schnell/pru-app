from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from pydantic import Field, field_validator

class Config:
    from_attributes = True #tells orm can access attributes

# child tables
class VehicleRegistrationContact(BaseModel):
    id: str
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationReciprocalIssued(BaseModel):
    id: str
    description: Optional[str] = None
    license_number: Optional[str] = None
    states: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationReciprocalReceived(BaseModel):
    id: str
    description: Optional[str] = None
    license_number: Optional[str] = None
    states: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationUnderCoverTrapInfo(BaseModel):
    id: str
    date: Optional[datetime] = None
    number: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationFictitiousTrapInfo(BaseModel):
    id: str
    date: Optional[datetime] = None
    number: Optional[str] = None
    
    class Config:
        from_attributes = True

# parent tables(these have their own child)
class VehicleRegistrationUnderCover(BaseModel):
    id: str
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    register_owner: Optional[str] = None
    status: Optional[str] = None
    
    #trap_info will be a LIST of the schema i defined above
    trap_info: List[VehicleRegistrationUnderCoverTrapInfo] = []
    
    class Config:
        from_attributes = True

class VehicleRegistrationFictitious(BaseModel):
    id: str
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    register_owner: Optional[str] = None
    status: Optional[str] = None
    
    trap_info: List[VehicleRegistrationFictitiousTrapInfo] = []
    
    class Config:
        from_attributes = True

# schemas for our main Master table
class VehicleRegistrationMasterBase(BaseModel):
    # These are all the columns from your model
    # exempted_license_plate: Optional[str] = None
    # license_number: Optional[str] = None
    # vehicle_id_number: Optional[str] = None
    # register_owner: Optional[str] = None
    # make: Optional[str] = None
    # model: Optional[str] = None
    # year: Optional[str] = None
    # status: str = "Pending"

    id: str = Field(alias="id")
    title: Optional[str] = None
    parent: str = Field(default="Vehicle Registration")
    list: str = Field(default="Master Record")
    key: str = Field(alias="vehicle_id_number")
    owner: str = Field(alias="registered_owner")
    submitted: datetime = Field(alias="created_at")
    status: str = Field(alias="approval_status")
    canApprove: bool = Field(default=True)
    
    class Config:
        from_attributes = True
        populate_by_name = True
    
    @field_validator('title', mode='before')
    @classmethod
    def compute_title(cls, v, info):
        vin = info.data.get('id', '')[:10] if info.data.get('id') else ''
        status = info.data.get('approval_status', 'Pending').capitalize()
        return f"{vin} • {status}"

# when we CREATE a new record
class VehicleRegistrationMasterCreate(VehicleRegistrationMasterBase):
    id: str  # Must provide VIN when creating

# reading a master record (the normal response)
class VehicleRegistrationMaster(VehicleRegistrationMasterBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# DETAILS schema -it inherits everything from VehicleRegistrationMaster and then adds all the nested lists
class VehicleRegistrationMasterDetails(VehicleRegistrationMaster):
    # These will be lists of the schemas we defined at the top
    contacts: List[VehicleRegistrationContact] = []
    reciprocal_issued: List[VehicleRegistrationReciprocalIssued] = []
    reciprocal_received: List[VehicleRegistrationReciprocalReceived] = []
    undercover_records: List[VehicleRegistrationUnderCover] = []
    fictitious_records: List[VehicleRegistrationFictitious] = []
    
    class Config:
        from_attributes = True

#Create/Update schemas for all those other tables

# main vehicle_registration_routes.py file needs these, so its POST/PUT routes kee working.
class VehicleRegistrationUnderCoverCreateBody(BaseModel):
    license_number: Optional[str]
    vehicle_id_number: Optional[str]
    register_owner: Optional[str]
    status: Optional[str] = "Pending"

class VehicleRegistrationFictitiousCreateBody(BaseModel):
    license_number: Optional[str]
    vehicle_id_number: Optional[str]
    register_owner: Optional[str]
    status: Optional[str] = "Pending"

class VehicleRegistrationContactCreateBody(BaseModel):
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class VehicleRegistrationReciprocalIssuedCreateBody(BaseModel):
    description: Optional[str] = None
    license_number: Optional[str] = None
    states: Optional[str] = None

class VehicleRegistrationReciprocalReceivedCreateBody(BaseModel):
    description: Optional[str] = None
    license_number: Optional[str] = None
    states: Optional[str] = None

class VehicleRegistrationUnderCoverTrapInfoCreateBody(BaseModel):
    date: Optional[datetime] = None
    number: Optional[str] = None

class VehicleRegistrationFictitiousTrapInfoCreateBody(BaseModel):
    date: Optional[datetime] = None
    number: Optional[str] = None



# ============================================================================
# NEW SCHEMAS FOR DYNAMIC TABLE SELECTION & RESPONSE FORMATTING
# ============================================================================

# when we CREATE a new record - with dynamic table selection
class VehicleRegistrationCreateRequest(BaseModel):
    # Master table fields (common to all tables)
    id: str  # VIN required for all record types
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    # vehicle info (optional)
    make: Optional[str] = None
    model: Optional[str] = None
    year_model: Optional[int] = None
    approval_status: Optional[str] = "Pending"
    # NEW: Select which table to insert into
    record_type: str = Field(default="master", description="master, undercover, or fictitious")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# LIST ITEM schema - same structure for all tables (master, undercover, fictitious)
class VehicleRegistrationListItem(BaseModel):
    id: str
    title: Optional[str] = None  # Computed field
    parent: str = Field(default="Vehicle Registration")
    list: str = Field(default="Master Record")
    key: str = Field(alias="vehicle_id_number")
    owner: str = Field(alias="registered_owner")
    submitted: datetime = Field(alias="created_at")
    status: str = Field(alias="approval_status")
    canApprove: bool = Field(default=True)
    record_type: str = Field(default="master", description="Which table this record belongs to")
    
    class Config:
        from_attributes = True
        populate_by_name = True
    
    @field_validator('title', mode='before')
    @classmethod
    def compute_title(cls, v, info):
        vin = info.data.get('id', '')[:10] if info.data.get('id') else ''
        status = info.data.get('approval_status', 'Pending').capitalize()
        return f"{vin} • {status}"


# RESPONSE schema - for after creating a record (all 3 tables)
class VehicleRegistrationResponse(BaseModel):
    id: str
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_model: Optional[int] = None
    approval_status: str
    created_at: datetime
    updated_at: datetime
    record_type: str = Field(default="master", description="Which table this record came from")
    
    class Config:
        from_attributes = True

