from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

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
    # These are all the columns from your model
    exempted_license_plate: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    register_owner: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = "Pending"

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

class VehicleRegistrationListItem(BaseModel):
    id: str # Formatted ID: "VR-YYYY-NNNNN"
    title: str # Formatted title
    parent: str = "Vehicle Registration" # Static value
    list_name: str = "Master Record" # Static value (maps to list/table name)
    key: str # Formatted key: "VIN: XXXXX..."
    owner: str # Formatted owner name: "J. Rivera"
    submitted: str # Formatted date: "YYYY-MM-DD"
    status: str # The approval_status field
    canApprove: bool # Logic based on status
    
    class Config:
        from_attributes = True # Allow creating from DB model attributes

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
