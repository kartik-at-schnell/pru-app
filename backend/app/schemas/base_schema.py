from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

DataType = TypeVar('DataType')

class ApiResponse(BaseModel, Generic[DataType]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[DataType] = None
    timestamp: Optional[str] = None  # optional, add if needed
