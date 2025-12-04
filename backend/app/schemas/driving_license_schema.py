from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# BASE Schemas

class DriverLicenseOriginalBase(BaseModel):
    active_status: Optional[bool] = None
    tfn: Optional[str] = None
    tln: Optional[str] = None
    tdl: Optional[str] = None
    ffn: Optional[str] = None
    fln: Optional[str] = None
    fdl: Optional[str] = None
    agency: Optional[str] = None
    contact: Optional[str] = None
    date_issued: Optional[date] = None
    modified: Optional[datetime] = None
    approval_status: Optional[str] = None 
    created_at: Optional[datetime] = None 
    created_by: Optional[int] = None  


class DriverLicenseContactBase(BaseModel):
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
    # date: Optional[date] = None
    number: Optional[str] = None
    fictitious_id: Optional[int] = None
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


# CREATE Schemas

class DriverLicenseOriginalCreate(BaseModel):
    # Required fields
    tfn: str = Field(..., description="True First Name")
    tln: str = Field(..., description="True Last Name")
    tdl: str = Field(..., description="True Driver License")
    
    active_status: Optional[bool] = None

    ffn: Optional[str] = None
    fln: Optional[str] = None
    fdl: Optional[str] = None
    
    agency: Optional[str] = None
    contact: Optional[str] = None
    date_issued: Optional[date] = None
    modified: Optional[datetime] = None
    approval_status: Optional[str] = None

    agency: Optional[str] = None


class DriverLicenseContactCreate(DriverLicenseContactBase):
    pass


class DriverLicenseFictitiousTrapCreate(DriverLicenseFictitiousTrapBase):
    pass


# UPDATE SCHEMAS

class DriverLicenseOriginalUpdate(BaseModel):
    active_status: Optional[bool] = None
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


# RESPONSE SCHEMAS

class DriverLicenseContactResponse(DriverLicenseContactBase):
    id: int
    original_record_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class DriverLicenseFictitiousTrapResponse(DriverLicenseFictitiousTrapBase):
    id: int
    original_record_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class DriverLicenseOriginalResponse(DriverLicenseOriginalBase):
    id: int
    active_status: Optional[bool] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class DriverLicenseOriginalDetailResponse(DriverLicenseOriginalBase):
    id: int
    active_status: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Relationships
    contacts: List[DriverLicenseContactResponse] = []
    fictitious_traps: List[DriverLicenseFictitiousTrapResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# request

class ApprovalStatusUpdate(BaseModel):
    approval_status: str = Field(..., description="True for approved, False for not approved")


class DeleteResponse(BaseModel):
    message: str


class RecordsCountResponse(BaseModel):
    total: int
    active: int
    inactive: int
    approved: int
    pending: int
    rejected: int

    
# search 
class DriverLicenseSearchQuery(BaseModel):
    id: Optional[int] = None
    tdl_number: Optional[str] = None
    fdl_number: Optional[str] = None
