from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Union
from pydantic import Field, field_validator
from sqlalchemy import func

class Config:
    from_attributes = True #tells orm can access attributes

# child tables
class VehicleRegistrationContact(BaseModel):
    id: int
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    alt_contact_1: Optional[str] = None
    alt_contact_2: Optional[str] = None
    alt_contact_3: Optional[str] = None
    alt_contact_4: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationReciprocalIssued(BaseModel):
    id: int
    master_record_id: Optional[int] = None
    description: Optional[str] = None
    license_plate: Optional[str] = None
    issuing_state: Optional[str] = None
    recipient_state: Optional[str] = None
    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    sticker_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    agreement_issued_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationReciprocalReceived(BaseModel):
    id: int
    master_record_id: Optional[int] = None
    description: Optional[str] = None
    license_plate: Optional[str] = None
    issuing_state: Optional[str] = None
    recipient_state: Optional[str] = None
    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    sticker_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationUnderCoverTrapInfo(BaseModel):
    id: int
    request_date: Optional[datetime] = None
    number: Optional[str] = None
    officer: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationFictitiousTrapInfo(BaseModel):
    id: int
    request_date: Optional[datetime] = None
    number: Optional[str] = None
    officer: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None
    
    
    model_config = ConfigDict(from_attributes=True)

# parent tables(these have their own child)
class VehicleRegistrationUnderCover(BaseModel):
    id: int
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    status: Optional[str] = None
    
    #trap_info will be a LIST of the schema i defined above
    trap_info: List[VehicleRegistrationUnderCoverTrapInfo] = []
    
    class Config:
        from_attributes = True

class VehicleRegistrationFictitious(BaseModel):
    id: int
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    status: Optional[str] = None
    
    trap_info: List[VehicleRegistrationFictitiousTrapInfo] = []
    
    class Config:
        from_attributes = True

# schemas for our main Master table
class VehicleRegistrationMasterBase(BaseModel):

    id: int = Field(alias="id")
    record_id: str = Field(alias="record_id")
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
    record_id: str = Field(alias="record_id")
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

class VehicleRegistrationMasterUpdate(BaseModel):
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_model: Optional[int] = None
    year_sold: Optional[int] = None
    body_type: Optional[str] = None
    type_license: Optional[str] = None
    type_vehicle: Optional[str] = None
    # category: Optional[str] = None
    active_status: Optional[bool] = None
    expiration_date: Optional[date] = None
    date_issued: Optional[date] = None
    date_received: Optional[date] = None
    date_fee_received: Optional[date] = None
    amount_paid: Optional[float] = None
    amount_due: Optional[float] = None
    amount_received: Optional[float] = None
    use_tax: Optional[float] = None
    sticker_issued: Optional[str] = None
    sticker_numbers: Optional[str] = None
    
    cert_type: Optional[str] = None
    mp: Optional[str] = None
    mo: Optional[str] = None
    axl: Optional[str] = None
    wc: Optional[str] = None
    cc_alco: Optional[str] = None
    
    approval_status: Optional[str] = None
    
    class Config:
        from_attributes = True

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
    registered_owner: Optional[str]
    status: Optional[str] = "Pending"
    officer: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationFictitiousCreateBody(BaseModel):
    license_number: Optional[str]
    vehicle_id_number: Optional[str]
    registered_owner: Optional[str]
    status: Optional[str] = "Pending"

    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationContactCreateBody(BaseModel):
    contact_name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    alt_contact_1: Optional[str] = None
    alt_contact_2: Optional[str] = None
    alt_contact_3: Optional[str] = None
    alt_contact_4: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationReciprocalIssuedCreateBody(BaseModel):
    master_record_id: Optional[int] = None
    description: Optional[str] = None
    license_number: Optional[str] = None
    issuing_state: Optional[str] = None
    recipient_state: Optional[str] = None
    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    sticker_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    agreement_issued_id: Optional[Union[str, int]] = None


    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('agreement_issued_id', mode='before')
    @classmethod
    def coerce_to_string_issued(cls, v):
        if v is not None:
            return str(v)
        return v

class VehicleRegistrationReciprocalReceivedCreateBody(BaseModel):
    master_record_id: Optional[int] = None
    agreement_received_id: Optional[Union[str, int]] = None
    description: Optional[str] = None
    license_number: Optional[str] = None
    issuing_state: Optional[str] = None
    recipient_state: Optional[str] = None
    year_of_renewal: Optional[int] = None
    cancellation_date: Optional[date] = None
    recieved_date: Optional[date] = None
    sticker_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    
    @field_validator('agreement_received_id', mode='before')
    @classmethod
    def coerce_to_string_received(cls, v):
        if v is not None:
            return str(v)
        return v

    @field_validator('cancellation_date', 'recieved_date', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v
    
    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationUnderCoverTrapInfoCreateBody(BaseModel):
    request_date: Optional[date] = None
    number: Optional[str] = None
    officer: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class VehicleRegistrationFictitiousTrapInfoCreateBody(BaseModel):
    request_date: Optional[date] = None
    number: Optional[str] = None
    officer: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# new schemas

#schemas for creating new records
class BaseVehicleRegistrationCreate(BaseModel):
    license_number: str
    registered_owner: str
    vehicle_id_number: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    make: Optional[str] = None
    year_model: Optional[int] = None
    year_sold: Optional[int] = None
    active_status: Optional[bool] = True
    expiration_date: Optional[date] = None
    date_issued : Optional[date] = None
    date_received : Optional[date] = None
    date_fee_received : Optional[date] = None
    amount_paid : Optional[float] = None
    amount_due : Optional[float] = None
    amount_received : Optional[float] = None
    use_tax : Optional[float] = None
    sticker_issued : Optional[str] = None
    sticker_numbers : Optional[str] = None
    body_type: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None

    cert_type : Optional[str] = None
    mp : Optional[str] = None
    mo : Optional[str] = None                           
    axl : Optional[str] = None
    wc : Optional[str] = None                       
    cc_alco : Optional[str] = None

class MasterCreateRequest(BaseVehicleRegistrationCreate):
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
    officer: Optional[str] = None
    cert_type: Optional[str] = None

class FictitiousCreateRequest(BaseVehicleRegistrationCreate):
    master_record_id: int
    vlp_class: Optional[str] = None
    amount_due: Optional[float] = None
    amount_received: Optional[float] = None
    class_type: Optional[str] = None
    type_license: Optional[str] = None
    expiration_date: Optional[date] = None
    date_fee_received: Optional[date] = func.now()
    amount_paid: Optional[float] = None
    officer: Optional[str] = None
    confidential_flag: Optional[bool] = False



class MasterDropdownResponse(BaseModel):
    id: str
    vehicle_id_number: str
    registered_owner: str

# bulk operations request schema
class BulkActionRequest(BaseModel):
    record_ids: List[str]  # Array of Master record primary keys (record_id)
    
    class Config:
        from_attributes = True

class BulkActionResponse(BaseModel):
    success_count: int
    failed_count: int
    failed_ids: List[str] = []
    message: str
    
    class Config:
        from_attributes = True

class VehicleRegistrationResponse(BaseModel):
    id: int
    record_id: str
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
    year_sold: Optional[int] = None
    cert_type: Optional[str] = None
    # document_id = Optional[int] = None
    error_text: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    date_received: Optional[date] = None
    date_issued: Optional[date] = None
    expiration_date: Optional[date] = None
    date_fee_received: Optional[date] = None
    amount_paid: Optional[Decimal] = None
    amount_due: Optional[Decimal] = None
    amount_received: Optional[Decimal] = None
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
    officer: Optional[str] = None
    active_status: Optional[bool]
    cert_type: Optional[str] = None
    
    class Config:
        from_attributes = True


# fc response
class VehicleRegistrationFictitiousResponse(VehicleRegistrationResponse):
    list: str = Field(default="Fictitious Record")
    master_record_id : Optional[int] = None
    officer: Optional[str] = None
    active_status: Optional[bool]
    confidential_flag: Optional[bool] = False
    
    class Config:
        from_attributes = True


class VehicleRegistrationUnderCoverUpdate(BaseModel):
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_model: Optional[int] = None
    year_sold: Optional[int] = None
    class_type: Optional[str] = None
    type_license: Optional[str] = None
    expiration_date: Optional[date] = None
    date_issued: Optional[date] = None
    date_fee_received: Optional[date] = None
    amount_paid: Optional[float] = None
    active_status: Optional[bool] = None
    officer: Optional[str] = None
    cert_type: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleRegistrationFictitiousUpdate(BaseModel):
    license_number: Optional[str] = None
    vehicle_id_number: Optional[str] = None
    registered_owner: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_model: Optional[int] = None
    year_sold: Optional[int] = None
    vlp_class: Optional[str] = None
    amount_due: Optional[float] = None
    amount_received: Optional[float] = None
    active_status: Optional[bool] = None
    officer: Optional[str] = None
    confidential_flag: Optional[bool] = False

    class Config:
        from_attributes = True

