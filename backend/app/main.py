from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import VehicleRegistrationMaster
from app.api.routes import vehicle_registration_routes
from app.api.routes import action_routes
from app.api.routes import dashboard_routes
from app.api.routes import auth_routes

from fastapi.staticfiles import StaticFiles

from app.api.routes import document_routes
from app.api.routes import driving_license_routes
from app.security import get_current_user
from app.api.routes import record_supression_routes


app = FastAPI()

#adding cors for FE connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)]
)

@app.get("/")
async def root():
    return {"message": "PRU API Live"}

@app.get("/health")
async def health():
    return {
        "status": 200,
        "message": "Server Running"
    }

router.include_router(document_routes.router)
router.include_router(vehicle_registration_routes.router)
router.include_router(driving_license_routes.router)
router.include_router(action_routes.router)
router.include_router(dashboard_routes.router)
router.include_router(record_supression_routes.router)

app.include_router(router)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Welcome to the PRU Automation API"}

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/test")
async def test(db: Session = Depends(get_db)):
    try:
        total_records = db.query(VehicleRegistrationMaster).count()
        pending = db.query(VehicleRegistrationMaster).filter(VehicleRegistrationMaster.approval_status == "pending").count()
        approved = db.query(VehicleRegistrationMaster).filter(VehicleRegistrationMaster.approval_status == "approved").count()
        rejected = db.query(VehicleRegistrationMaster).filter(VehicleRegistrationMaster.approval_status == "rejected").count()

        sample_records = db.query(VehicleRegistrationMaster).limit(5).all()

        return{
            "db_status": "connected",
            "total_records": total_records,
            "status_breakdown": {
                "pending": pending,
                "approved": approved,
                "rejected": rejected
            },
            "sample_records":[
                
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
        return {
            "db_status": "error", "error": str(e)
        }
        
