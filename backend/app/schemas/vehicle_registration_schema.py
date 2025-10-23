from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class VehicleRegistrationBase(BaseModel):
    license_number: str
    registered_owner: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = "California"
    zip_code: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_model: Optional[int] = None
    body_type: Optional[str] = None
    type_license: Optional[str] = None
    type_vehicle: Optional[str] = None
    category: Optional[str] = None
    expiration_date: Optional[date] = None
    date_issued: Optional[date] = None
    date_fee_received: Optional[date] = None
    amount_paid: Optional[float] = None
    use_tax: Optional[float] = None
    sticker_issued: Optional[str] = None
    sticker_numbers: Optional[str] = None
    approval_status: Optional[str] = "pending"
    active_status: Optional[bool] = True
    description: Optional[str] = None

# fro creating new record
class VehicleRegistrationCreate(VehicleRegistrationBase):
    pass

#for updating records
class VehicleRegistrationUpdate(VehicleRegistrationBase):
    pass

# schema for response output
class VehicleRegistrationOut(VehicleRegistrationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


