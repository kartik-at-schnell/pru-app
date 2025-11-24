from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models import VehicleRegistrationMaster

# NEW — correct header-based auth
from fastapi.security.api_key import APIKeyHeader
from app.security import get_current_user

# Routers
from app.api.routes import (
    vehicle_registration_routes,
    action_routes,
    dashboard_routes,
    document_routes,
    driving_license_routes,
    auth_routes
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
app = FastAPI(
    title="PRU Automation API",
    description="DMV PRU Backend API with RBAC",
    version="1.0.0"
)

# -------------------------------------------------------------------
#  CORS
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
#  Authentication for Swagger (Header-based)
# -------------------------------------------------------------------
XUserEmail = APIKeyHeader(
    name="X-User-Email",
    auto_error=False
)

def swagger_current_user(email: str = Depends(XUserEmail)):
    """Swagger-only authentication using X-User-Email"""
    return {"email": email}

# -------------------------------------------------------------------
#  Public Routes
# -------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": 200, "message": "Server Running"}

@app.get("/")
async def root():
    return {"message": "PRU API Live"}

# -------------------------------------------------------------------
#  Protected Router  (ALL API endpoints under /api require user)
# -------------------------------------------------------------------
protected_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)]    # Backend auth + RBAC
)

# Include feature routers
protected_router.include_router(document_routes.router)
protected_router.include_router(vehicle_registration_routes.router)
protected_router.include_router(driving_license_routes.router)
protected_router.include_router(action_routes.router)
protected_router.include_router(dashboard_routes.router)

# Add Protected Routes to App
app.include_router(protected_router)

# Authentication routes (if any)
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

# -------------------------------------------------------------------
#  STATIC FILES
# -------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# -------------------------------------------------------------------
# Test Route to Verify Database
# -------------------------------------------------------------------
@app.get("/test")
async def test(db: Session = Depends(get_db)):

    try:
        total_records = db.query(VehicleRegistrationMaster).count()
        pending = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.approval_status == "pending"
        ).count()
        approved = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.approval_status == "approved"
        ).count()
        rejected = db.query(VehicleRegistrationMaster).filter(
            VehicleRegistrationMaster.approval_status == "rejected"
        ).count()

        sample_records = db.query(VehicleRegistrationMaster).limit(5).all()

        return {
            "db_status": "connected",
            "total_records": total_records,
            "status_breakdown": {
                "pending": pending,
                "approved": approved,
                "rejected": rejected
            },
            "sample_records": [
                {
                    "id": record.id,
                    "license_number": record.license_number,
                    "registered_owner": record.registered_owner,
                    "make": record.make,
                    "model": record.model,
                    "approval_status": record.approval_status,
                    "created_at": record.created_at.isoformat()
                }
                for record in sample_records
            ]
        }

    except Exception as e:
        return {"db_status": "error", "error": str(e)}
