from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from pydantic import Field, field_validator
from sqlalchemy import func

from app.models.vehicle_registration import VehicleRegistrationReciprocalReceived

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

# --- UPDATED RECIPROCAL READ SCHEMA (Used in Details View) ---
class  VehicleRegistrationReciprocalIssuedRead(BaseModel):
    id: int
    master_record_id: Optional[int] = None
    description: str
    license_plate: str          # Renamed from license_number
    state: str                  # Renamed from states
    year_of_renewal: int
    cancellation_date: Optional[date] = None
    sticker_number: Optional[str] = None
    
    # # New Fields
    # issuing_authority: str
    # issuing_state: str
    # recipent_state: str
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class VehicleRegistrationReciprocalReceivedResponse(BaseModel):
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
    contacts: List[VehicleRegistrationContact] = []
    reciprocal_received: List[VehicleRegistrationReciprocalReceived] = []
    reciprocal_received: List[VehicleRegistrationReciprocalReceivedResponse] = Field(default_factory=list)
    undercover_records: List[VehicleRegistrationUnderCover] = []
    fictitious_records: List[VehicleRegistrationFictitious] = []
    
    class Config:
        from_attributes = True


#Create/Update schemas for all those other tables

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
    master_record_id: Optional[int] = None
    description: str
    license_plate: str
    state: str
    year_of_renewal: int
    cancellation_date: Optional[date] = None
    sticker_number: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


# --- UPDATED RECIPROCAL RESPONSE ---
class VehicleRegistrationReciprocalIssuedResponse(VehicleRegistrationReciprocalIssuedCreateBody):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- UPDATED RECIPROCAL UPDATE BODY ---
class VehicleRegistrationReciprocalIssuedUpdate(BaseModel):
    description: Optional[str] = None
    license_plate: Optional[str] = None
    state: Optional[str] = None
    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    sticker_number: Optional[str] = None
    # issuing_authority: Optional[str] = None
    # issuing_state: Optional[str] = None
    # recipent_state: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Apply validators to update model as well
    @field_validator('year_of_renewal')
    def validate_year(cls, v):
        if v is None: return v
        current_year = datetime.now().year
        if v < current_year:
            raise ValueError(f"Year of renewal ({v}) must be current or future year")
        return v

    # @field_validator('issuing_state', 'recipent_state')
    # def validate_state_code(cls, v):
    #     if v is None: return v
    #     if len(v) != 2 or not v.isalpha():
    #         raise ValueError(f"State code ({v}) must be exactly 2 letters")
    #     return v.upper() 


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

# new schemas
class BaseVehicleRegistrationCreate(BaseModel):
    license_number: str
    registered_owner: str
    vehicle_id_number: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    make: Optional[str] = None
    year_model: Optional[str] = None
    active_status: Optional[bool] = True

class MasterCreateRequest(BaseVehicleRegistrationCreate):
    model: Optional[str] = None
    body_type: Optional[str]
    type_license: Optional[str] = None
    type_vehicle: Optional[str] = None

class UnderCoverCreateRequest(BaseVehicleRegistrationCreate):
    master_record_id: int
    class_type: Optional[str] = None
    type_license: Optional[str] = None
    expiration_date: Optional[date] = None
    date_issued: Optional[date] = None
    date_fee_received: Optional[date] = func.now()
    amount_paid: Optional[float] = None

class FictitiousCreateRequest(BaseVehicleRegistrationCreate):
    master_record_id: int
    model: Optional[str] = None
    vlp_class: str
    amount_due: Optional[float] = None
    amount_received: Optional[float] = None


class MasterDropdownResponse(BaseModel):
    id: str
    vehicle_id_number: str
    registered_owner: str

class UnderCoverResponse(BaseModel):
    id: int
    master_record_id: str
    vehicle_id_number: str
    license_number: Optional[str]
    registered_owner: Optional[str]
    active_status: bool
    
    class Config:
        from_attributes = True

class FictitiousResponse(BaseModel):
    id: int
    master_record_id: str
    vehicle_id_number: str  # auto-fetched from master
    license_number: Optional[str]
    registered_owner: Optional[str]
    active_status: bool
    
    class Config:
        from_attributes = True

# bulk operations request schema
class BulkActionRequest(BaseModel):
    record_ids: List[int]  # Array of Master record primary keys
    
    class Config:
        from_attributes = True

class BulkActionResponse(BaseModel):
    success_count: int
    failed_count: int
    failed_ids: List[int] = []
    message: str
    
    class Config:
        from_attributes = True

class VehicleRegistrationResponse(BaseModel):
    id: int
    license_number: str
    vehicle_id_number: str
    active_status: bool
    registered_owner: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    make: Optional[str] = None
    year_model: Optional[int] = None
    class_type: Optional[str] = None
    type_license: Optional[str] = None
    type_vehicle: Optional[str] = None
    model: Optional[str] = None
    body_type: Optional[str] = None
    category: Optional[str] = None
    # document_id = Optional[int] = None
    error_text: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    date_recieved: Optional[date] = None
    date_issued: Optional[date] = None
    expiration_date: Optional[date] = None
    date_fee_recieved: Optional[date] = None
    amount_paid: Optional[Decimal] = None
    amount_due: Optional[Decimal] = None
    amount_recieved: Optional[Decimal] = None
    use_tax: Optional[int] = None
    sticker_issued: Optional[str] = None
    sticker_numbers: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    description: Optional[str] = None
    parent: str = Field(default="Vehicle Registration")    
    class Config:
        from_attributes = True
        populate_by_name = True  

class VehicleRegistrationMasterResponse(VehicleRegistrationResponse):
    approval_status: Optional[str] = None
    list: str = Field(default="Master Record")
    active_status: Optional[bool]
    
    class Config:
        from_attributes = True

# uc response
class VehicleRegistrationUnderCoverResponse(VehicleRegistrationResponse):
    list: str = Field(default="Undercover Record")
    master_record_id : Optional[int] = None
    active_status: Optional[bool]
    
    class Config:
        from_attributes = True


# fc response
class VehicleRegistrationFictitiousResponse(VehicleRegistrationResponse):
    list: str = Field(default="Fictitious Record")
    master_record_id : Optional[int] = None
    active_status: Optional[bool]
    
    class Config:
        from_attributes = True
        
class VRReciprocalReceivedCreate(BaseModel):
    registered_owner: str
    owner_address: str
    description: str
    license_plate: str
    sticker_number: Optional[str] = None

    year_of_renewal: int
    cancellation_date: Optional[date] = None
    recieved_date: date   # use EXACT spelling from model
    expiry_date: date

    issuing_authority: str
    issuing_state: str
    recipent_state: str   # EXACT model field spelling

    created_by: Optional[str] = None

    class Config:
        from_attributes = True
        
class VRReciprocalReceivedResponse(BaseModel):
    id: int
    registered_owner: Optional[str] = None
    owner_address: Optional[str] = None
    description: Optional[str] = None
    license_plate: Optional[str] = None
    sticker_number: Optional[str] = None

    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    recieved_date: Optional[date] = None
    expiry_date: Optional[date] = None

    issuing_authority: Optional[str] = None
    issuing_state: Optional[str] = None
    recipent_state: Optional[str] = None

    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# class VehicleRegistrationReciprocalReceivedCreateBody(BaseModel):
#     master_record_id: int
#     description: str
#     license_plate: str
#     issuing_state: str
#     recipient_state: str
#     year_of_renewal: int

#     received_date: date
#     expiry_date: date

#     cancellation_date: Optional[date] = None
#     sticker_number: Optional[str] = None

#     registered_owner: Optional[str] = None
#     owner_address: Optional[str] = None

#     created_by: str

#     class Config:
#         from_attributes = True


class VRReciprocalReceivedUpdate(BaseModel):
    registered_owner: Optional[str] = None
    owner_address: Optional[str] = None
    description: Optional[str] = None
    license_plate: Optional[str] = None
    sticker_number: Optional[str] = None

    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    recieved_date: Optional[date] = None       # MISSING
    expiry_date: Optional[date] = None

    issuing_authority: Optional[str] = None    # MISSING
    issuing_state: Optional[str] = None
    recipent_state: Optional[str] = None       # MISSING

    class Config:
        from_attributes = True


class VRContactCreate(BaseModel):
    master_record_id: int
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

    alt_contact_1: Optional[str] = None
    alt_contact_2: Optional[str] = None
    alt_contact_3: Optional[str] = None
    alt_contact_4: Optional[str] = None

class VRContactUpdate(BaseModel):
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

    alt_contact_1: Optional[str] = None
    alt_contact_2: Optional[str] = None
    alt_contact_3: Optional[str] = None
    alt_contact_4: Optional[str] = None

class VRContactResponse(BaseModel):
    id: int
    master_record_id: int
    contact_name: Optional[str]
    department: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    alt_contact_1: Optional[str]
    alt_contact_2: Optional[str]
    alt_contact_3: Optional[str]
    alt_contact_4: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UCTrapInfoCreate(BaseModel):
    undercover_id: int
    date: date
    number: Optional[str] = None
    officer_name: Optional[str] = None
    location: Optional[str] = None
    details: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[date] = None

class UCTrapInfoUpdate(BaseModel):
    date: Optional[date] = None
    number: Optional[str] = None
    officer_name: Optional[str] = None
    location: Optional[str] = None
    details: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[date] = None  

class UCTrapInfoResponse(BaseModel):
    id: int
    undercover_id: int
    date: date
    number: Optional[str]
    officer_name: Optional[str]
    location: Optional[str]
    details: Optional[str]
    verified_by: Optional[str]
    verification_date: Optional[date] = None

    class Config:
        from_attributes = True

class FictitiousTrapInfoCreate(BaseModel):
    fictitious_id: int
    date: Optional[date] = None
    number: Optional[str] = None
    location: Optional[str] = None
    officer: Optional[str] = None
    reason: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[date] = None
  


class FictitiousTrapInfoUpdate(BaseModel):
    date: Optional[date] = None
    number: Optional[str] = None
    location: Optional[str] = None
    officer: Optional[str] = None
    reason: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[date] = None
 


class FictitiousTrapInfoResponse(BaseModel):
    id: int
    fictitious_id: int
    date: Optional[date]
    number: Optional[str]
    location: Optional[str]
    officer: Optional[str]
    reason: Optional[str]
    verified_by: Optional[str]
    verification_date: Optional[date]


    class Config:
        from_attributes = True


        

# class VehicleRegistrationReciprocalReceivedResponse(BaseModel):
#     id: int
#     master_record_id: int
#     description: str
#     license_plate: str
#     issuing_state: str
#     recipient_state: str
#     year_of_renewal: int
#     received_date: date
#     expiry_date: date

#     cancellation_date: Optional[date]
#     sticker_number: Optional[str]
#     registered_owner: Optional[str]
#     owner_address: Optional[str]

#     created_by: str
#     created_at: datetime
#     updated_by: Optional[str]
#     updated_at: Optional[datetime]

#     class Config:
#         from_attributes = True

# VehicleRegistrationMasterDetails.model_rebuild()
# VehicleRegistrationReciprocalIssuedResponse.model_rebuild()       