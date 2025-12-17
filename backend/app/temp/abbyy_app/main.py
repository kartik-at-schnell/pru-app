import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import jwt

from app.temp.abbyy_app.abbyy_database import get_db, DriverLicense, VehicleRegistration
from app.temp.abbyy_app.extractor import extract_and_store_abbyy_response

MOCK_DATA_DIR = "mock_abbyy_responses"
Path(MOCK_DATA_DIR).mkdir(parents=True, exist_ok=True)

SECRET_KEY = "abbyy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 525600  # 1 YEAR

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UploadResponse(BaseModel):
    status: str
    message: str
    file_path: str
    extracted: dict = Field(default_factory=dict)


class ListResponseModel(BaseModel):
    status: str
    count: int
    files: list


class HealthCheckModel(BaseModel):
    status: str
    service: str


class DriverLicenseResponse(BaseModel):
    id: int
    tn_dl: str
    first_first_name: str
    first_last_name: str
    date_issued: datetime
    expiration_date: datetime
    agency: str
    batch_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleRegistrationResponse(BaseModel):
    id: int
    vin: str
    license_plate: str
    make: str
    year_model: str
    registered_owner: str
    date_issued: datetime
    expiration_date: datetime
    batch_id: str
    created_at: datetime

    class Config:
        from_attributes = True


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: no username")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI(
    title="ABBYY Mock OCR Service",
    description="Mock ABBYY OCR service with database extraction.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


@app.get("/health", response_model=HealthCheckModel)
async def health_check():
    return HealthCheckModel(status="healthy", service="ABBYY Mock OCR Service")


@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    if request.username != VALID_USERNAME or request.password != VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": request.username}, expires_delta=expires)

    return TokenResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
    )


@app.post("/upload", response_model=UploadResponse)
async def upload(
    json_payload: dict = Body(...),
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        batch_id = json_payload.get("BatchId", f"batch_{uuid.uuid4().hex[:8]}")
        filename = f"{batch_id}_{timestamp}.json"
        filepath = os.path.join(MOCK_DATA_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_payload, f, indent=2, ensure_ascii=False)

        extracted = extract_and_store_abbyy_response(db, batch_id, json_payload)

        return UploadResponse(
            status="success",
            message=f"JSON saved to {filename} & fields extracted to database",
            file_path=filepath,
            extracted=extracted
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list", response_model=ListResponseModel)
async def list_files(username: str = Depends(verify_token)):
    try:
        files = [f for f in os.listdir(MOCK_DATA_DIR) if f.endswith(".json")]
        return ListResponseModel(status="success", count=len(files), files=sorted(files, reverse=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/driver-licenses", response_model=List[DriverLicenseResponse])
async def get_driver_licenses(username: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        return db.query(DriverLicense).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/driver-licenses/{license_id}", response_model=DriverLicenseResponse)
async def get_driver_license(license_id: int, username: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        record = db.query(DriverLicense).filter(DriverLicense.id == license_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Driver license not found")
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vehicles", response_model=List[VehicleRegistrationResponse])
async def get_vehicles(username: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        return db.query(VehicleRegistration).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vehicles/{vehicle_id}", response_model=VehicleRegistrationResponse)
async def get_vehicle(vehicle_id: int, username: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        record = db.query(VehicleRegistration).filter(VehicleRegistration.id == vehicle_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vehicles/vin/{vin}", response_model=VehicleRegistrationResponse)
async def get_vehicle_by_vin(vin: str, username: str = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        record = db.query(VehicleRegistration).filter(VehicleRegistration.vin == vin).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Vehicle with VIN {vin} not found")
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
