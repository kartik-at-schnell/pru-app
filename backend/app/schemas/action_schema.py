from pydantic import BaseModel
from typing import Optional
from datetime import datetime

#incoming request valiidation schema

class ActionRequest(BaseModel):
    record_id: int
    rocord_table: str
    action_type: str
    user_id: Optional[int] = 1
    notes: Optional[str]= None

#response schema
class ActionResponse(BaseModel):
    success: bool
    message: str
    record_id: int
    new_status: str
    action_logged: bool
    time_stamp: datetime

    class Config:
        orm_mode = True #makes aut conversion from sqlAlc obj to json

# schema to view action logs
class ActionLogOut(BaseModel):
    id: int
    record_table: str
    record_id: int
    action_type_name: str
    user_id: int
    notes: Optional[str] = None
    created_at: datetime
    ip_address: Optional[str] = None

    class Config:
        orm_mode = True

