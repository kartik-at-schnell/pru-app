from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from pydantic import Field, field_validator

class Config:
    from_attributes = True #tells orm can access attributes

# child tables
class VehicleRegistrationContact(BaseModel):
    id: int
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationReciprocalIssued(BaseModel):
    id: int
    description: Optional[str] = None
    license_number: Optional[str] = None
    states: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationReciprocalReceived(BaseModel):
    id: int
    description: Optional[str] = None
    license_number: Optional[str] = None
    states: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationUnderCoverTrapInfo(BaseModel):
    id: int
    date: Optional[datetime] = None
    number: Optional[str] = None
    
    class Config:
        from_attributes = True

class VehicleRegistrationFictitiousTrapInfo(BaseModel):
    id: int
    date: Optional[datetime] = None
    number: Optional[str] = None
    
    class Config:
        from_attributes = True

# parent tables(these have their own child)
class VehicleRegistrationUnderCover(BaseModel):
    id: int
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    register_owner: Optional[str] = None
    status: Optional[str] = None
    
    #trap_info will be a LIST of the schema i defined above
    trap_info: List[VehicleRegistrationUnderCoverTrapInfo] = []
    
    class Config:
        from_attributes = True

class VehicleRegistrationFictitious(BaseModel):
    id: int
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    register_owner: Optional[str] = None
    status: Optional[str] = None
    
    trap_info: List[VehicleRegistrationFictitiousTrapInfo] = []
    
    class Config:
        from_attributes = True

# schemas for our main Master table
class VehicleRegistrationMasterBase(BaseModel):

    id: int = Field(alias="id")
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
        vin = str(info.data.get('id', 'N/A')).zfill(4) if info.data.get('id') else 'N/A'
        status = info.data.get('approval_status', 'Pending').capitalize()
        return f"{vin} • {status}"


    id: int = Field(alias="id")
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
        vin = str(info.data.get('id', 'N/A')).zfill(4) if info.data.get('id') else 'N/A'
        status = info.data.get('approval_status', 'Pending').capitalize()
        return f"{vin} • {status}"

# when we CREATE a new record
class VehicleRegistrationMasterCreate(BaseModel):
    license_number: str
    vehicle_id_number: str
    registered_owner: str
    address: str
    city: str
    state: str = "California"
    zip_code: str
    make: str
    model: str
    year_model: int
    body_type: Optional[str] = None
    type_license: Optional[str] = None
    type_vehicle: Optional[str] = None
    category: Optional[str] = None
    expiration_date: Optional[date] = None
    date_issued: Optional[date] = None
    approval_status: str = "pending"

    class Config:
        from_attributes = True

# reading a master record (the normal response)
class VehicleRegistrationMaster(VehicleRegistrationMasterBase):
    id: int
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