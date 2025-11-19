from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# BASE SCHEMAS

class DriverLicenseOriginalBase(BaseModel):
    """Base schema for Driver License Original Record"""
    status: Optional[str] = None
    tln: str = Field(..., description="True License Number - Required")
    tfn: str = Field(..., description="True First Name - Required")
    tdl: str = Field(..., description="True Driver License - Required")
    fln: Optional[str] = Field(None, description="Fake License Number - Optional")
    ffn: Optional[str] = Field(None, description="Fake First Name - Optional")
    fdl: Optional[str] = Field(None, description="Fake Driver License - Optional")
    agency: Optional[str] = None
    contact: Optional[str] = None
    date_issued: Optional[date] = None
    modified: Optional[datetime] = None


class DriverLicenseContactBase(BaseModel):
    """Base schema for Driver License Contact"""
    content_type_id: Optional[str] = None
    title: Optional[str] = None
    modified: Optional[datetime] = None
    created: Optional[datetime] = None
    author_id: Optional[int] = None
    editor_id: Optional[int] = None
    odata_ui_version_string: Optional[str] = None
    attachments: Optional[bool] = None
    guid: Optional[str] = None
    compliance_asset_id: Optional[str] = None
    contact_name: Optional[str] = None
    department1: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    alternative_contact1: Optional[str] = None
    alternative_contact2: Optional[str] = None
    alternative_contact3: Optional[str] = None
    alternative_contact4: Optional[str] = None
    odata_color_tag: Optional[str] = None


class DriverLicenseFictitiousTrapBase(BaseModel):
    """Base schema for Driver License Fictitious Trap"""
    date: Optional[date] = None
    number: Optional[str] = None
    fictitious_id_2: Optional[int] = None
    test: Optional[str] = None
    title: Optional[str] = None
    compliance_asset_id: Optional[str] = None
    color_tag: Optional[str] = None
    test2: Optional[str] = None
    content_type: Optional[str] = None
    modified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    version: Optional[str] = None
    attachments: Optional[bool] = None
    type: Optional[str] = None
    item_child_count: Optional[int] = None
    folder_child_count: Optional[int] = None
    label_setting: Optional[str] = None
    retention_label: Optional[str] = None
    retention_label_applied: Optional[date] = None
    label_applied_by: Optional[str] = None
    item_is_record: Optional[bool] = None
    app_created_by: Optional[str] = None
    app_modified_by: Optional[str] = None


# CREATE SCHEMAS

class DriverLicenseOriginalCreate(DriverLicenseOriginalBase):
    """Schema for creating a new driver license original record"""
    pass


class DriverLicenseContactCreate(DriverLicenseContactBase):
    """Schema for creating a new contact"""
    pass


class DriverLicenseFictitiousTrapCreate(DriverLicenseFictitiousTrapBase):
    """Schema for creating a new fictitious trap"""
    pass


# UPDATE SCHEMAS

class DriverLicenseOriginalUpdate(BaseModel):
    """Schema for updating driver license original record - all fields optional"""
    status: Optional[str] = None
    tln: Optional[str] = None
    tfn: Optional[str] = None
    tdl: Optional[str] = None
    fln: Optional[str] = None
    ffn: Optional[str] = None
    fdl: Optional[str] = None
    agency: Optional[str] = None
    contact: Optional[str] = None
    date_issued: Optional[date] = None
    modified: Optional[datetime] = None
    approval_status: Optional[str] = None
    active_status: Optional[bool] = None


# RESPONSE SCHEMAS

class DriverLicenseContactResponse(DriverLicenseContactBase):
    """Response schema for contact - includes ID"""
    id: int
    original_record_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class DriverLicenseFictitiousTrapResponse(DriverLicenseFictitiousTrapBase):
    """Response schema for fictitious trap - includes ID"""
    id: int
    original_record_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class DriverLicenseOriginalResponse(DriverLicenseOriginalBase):
    """Response schema for original record - simple (for list views)"""
    id: int
    approval_status: Optional[str] = None
    active_status: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DriverLicenseOriginalDetailResponse(DriverLicenseOriginalBase):
    """Detailed response schema - includes relationships (for single record view)"""
    id: int
    approval_status: Optional[str] = None
    active_status: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Relationships
    contacts: List[DriverLicenseContactResponse] = []
    fictitious_traps: List[DriverLicenseFictitiousTrapResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# request

class ApprovalStatusUpdate(BaseModel):
    """Schema for updating approval status (action tracking TODO for later)"""
    approval_status: str = Field(..., pattern="^(pending|approved|rejected|on_hold)$")


class DeleteResponse(BaseModel):
    """Standard delete response"""
    message: str


class RecordsCountResponse(BaseModel):
    """Response schema for records count statistics"""
    total: int
    active: int
    inactive: int
    pending_approval: int
    approved: int
    rejected: int