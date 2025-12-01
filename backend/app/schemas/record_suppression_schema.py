from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# detailed 1

class SuppressionDetail1Base(BaseModel):

    date_requested: Optional[datetime] = None
    driver_license_vehicle_plate: Optional[str] = None
    person_requesting_access: str
    reason: str
    amount_of_time_open: str
    initials: Optional[str] = None

class SuppressionDetail1Create(SuppressionDetail1Base):

    pass

class SuppressionDetail1Response(SuppressionDetail1Base):
    
    id: int
    suppression_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# detailed 2

class SuppressionDetail2Base(BaseModel):
    old_name: Optional[str] = None
    old_driver_license_vehicle_plate: Optional[str] = None

class SuppressionDetail2Create(SuppressionDetail2Base):

    pass

class SuppressionDetail2Response(SuppressionDetail2Base):

    id: int
    suppression_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# master schemas

class RecordSuppressionBase(BaseModel):
    record_type: Optional[str] = Field(None, description="vr_master, dl_original, dl_fictitious, or None if no linking")
    record_id: Optional[int] = Field(None, description="Optional link to actual VR/DL record")
    reason: str
    reason_description: Optional[str] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None

class RecordSuppressionCreate(RecordSuppressionBase):
    created_by: str

class RecordSuppressionUpdate(BaseModel):
    reason: Optional[str] = None
    reason_description: Optional[str] = None
    expiration_date: Optional[date] = None
    status: Optional[str] = None

class RecordSuppressionResponse(RecordSuppressionBase):
    id: int
    status: str
    is_active: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RecordSuppressionDetailedResponse(RecordSuppressionResponse):
    details_1: List[SuppressionDetail1Response] = []
    details_2: List[SuppressionDetail2Response] = []
    
    class Config:
        from_attributes = True
