# app/schemas/agency_schema.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# Agency schemas
class AgencyCreate(BaseModel):
    agency_name: str = Field(..., max_length=100)
    agency_code: Optional[str] = Field(None, max_length=50)
    agency_type_id: int
    status: Optional[str] = Field(default="Active")
    #description: Optional[str] = Field(None, max_length=500)
    #contact_email: Optional[EmailStr] = None
    #contact_phone: Optional[str] = Field(None, max_length=20)
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AgencyUpdate(BaseModel):
    agency_name: Optional[str] = Field(None, max_length=100)
    agency_code: Optional[str] = Field(None, max_length=50)
    agency_type_id: Optional[int] = None
    status: Optional[str] = None
    #description: Optional[str] = Field(None, max_length=500)
    #contact_email: Optional[EmailStr] = None
    #contact_phone: Optional[str] = Field(None, max_length=20)
    modified_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AgencyResponse(BaseModel):
    id: int
    agency_name: str
    agency_code: Optional[str] = None
    agency_type_id: int
    status: str
    #description: Optional[str] = None
    #contact_email: Optional[str] = None
    #contact_phone: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# AgencyType schemas
class AgencyTypeCreate(BaseModel):
    type_name: str = Field(..., max_length=50)
    type_description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(default="Active")
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AgencyTypeResponse(BaseModel):
    id: int
    type_name: str
    type_description: Optional[str] = None
    status: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)



# AgencyOrder schemas
class AgencyOrderCreate(BaseModel):
    agency_id: int
    display_context: str = Field(..., max_length=50)
    order_sequence: int = Field(..., ge=0)
    is_default: Optional[bool] = False
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AgencyOrderResponse(BaseModel):
    id: int
    agency_id: int
    display_context: str
    order_sequence: int
    is_default: Optional[bool] = False
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Search
class AgencyListQuery(BaseModel):
    search: Optional[str] = None
    agency_type_id: Optional[int] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    #skip: Optional[int] = 0
    #limit: Optional[int] = 100

    model_config = ConfigDict(from_attributes=True)
