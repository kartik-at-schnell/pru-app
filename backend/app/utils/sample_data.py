# this is entirely vibe-coded

from faker import Faker
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random
from app.models import (
    VehicleRegistrationMaster, 
    ActionType,
    VehicleRegistrationUnderCover,
    VehicleRegistrationFictitious
)

fake = Faker('en_US')

# California-specific data
CALIFORNIA_CITIES = [
    "Los Angeles", "San Francisco", "San Diego", "Sacramento", "Oakland",
    "Fresno", "Long Beach", "Santa Ana", "Anaheim", "Riverside",
    "Bakersfield", "Stockton", "Chula Vista", "Fremont", "San Jose"
]

CAR_MAKES = [
    "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz",
    "Audi", "Volkswagen", "Hyundai", "Kia", "Subaru", "Mazda", "Lexus"
]

def generate_california_license_plate():
    """Generate realistic California license plate"""
    formats = [
        f"{random.randint(1,9)}{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(100,999)}",  # 1ABC123
        f"{random.randint(10,99)}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(100,999)}",  # 12AB123
        f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(1000,9999)}",  # ABC1234
    ]
    return random.choice(formats)

def generate_vin():
    """Generate realistic 17-character VIN"""
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ1234567890"  # No I, O, Q
    return ''.join(random.choice(chars) for _ in range(17))

def create_action_types(db: Session):
    """Create basic action types"""
    actions = [
        {"name": "approve", "description": "Record approved by officer"},
        {"name": "reject", "description": "Record rejected due to errors"},
        {"name": "hold", "description": "Record placed on hold for review"},
        {"name": "reprocess", "description": "Record sent back for reprocessing"},
    ]
    
    for action_data in actions:
        # Check if already exists
        existing = db.query(ActionType).filter(ActionType.name == action_data["name"]).first()
        if not existing:
            action = ActionType(**action_data)
            db.add(action)
    
    db.commit()
    print("✅ Action types created")

def create_vehicle_registration_samples(db: Session, count: int = 80):
    """Create realistic California vehicle registration records"""
    
    # Create different status distributions
    statuses = ["pending"] * 50 + ["approved"] * 20 + ["rejected"] * 10
    random.shuffle(statuses)
    
    for i in range(count):
        # Generate realistic data
        city = random.choice(CALIFORNIA_CITIES)
        make = random.choice(CAR_MAKES)
        model = fake.word().title() + " " + fake.word().title()
        year = random.randint(2010, 2024)
        
        record = VehicleRegistrationMaster(
            # Basic Information
            license_number=generate_california_license_plate(),
            vehicle_id_number=generate_vin(),
            registered_owner=fake.name(),
            
            # Address
            address=fake.street_address(),
            city=city,
            state="California",
            zip_code=fake.zipcode_in_state("CA"),
            
            # Vehicle Details
            make=make,
            model=model,
            year_model=year,
            body_type=random.choice(["Sedan", "SUV", "Truck", "Coupe", "Hatchback", "Convertible"]),
            type_license=random.choice(["Regular", "Commercial", "Motorcycle", "Trailer"]),
            type_vehicle=random.choice(["Passenger", "Commercial", "Motorcycle", "Truck"]),
            category=random.choice(["Personal", "Business", "Government"]),
            
            # Registration Details
            expiration_date=fake.date_between(start_date=date.today(), end_date=date.today() + timedelta(days=365*2)),
            date_issued=fake.date_between(start_date=date.today() - timedelta(days=365), end_date=date.today()),
            date_fee_received=fake.date_between(start_date=date.today() - timedelta(days=30), end_date=date.today()),
            amount_paid=round(random.uniform(50.0, 500.0), 2),
            use_tax=round(random.uniform(0.0, 50.0), 2),
            sticker_issued=f"ST{random.randint(100000, 999999)}",
            sticker_numbers=f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            
            # System Fields
            approval_status=statuses[i % len(statuses)] if i < len(statuses) else "pending",
            active_status=True,
            record_type="master",
            description=f"Vehicle registration for {make} {model} {year}",
        )
        
        db.add(record)
        
        # Every 10th record, create an undercover version
        if i % 10 == 0:
            undercover = VehicleRegistrationUnderCover(
                master_record_id=None,  # Will be set after master is saved
                license_number=generate_california_license_plate(),
                vehicle_id_number=generate_vin(),
                registered_owner="CONFIDENTIAL AGENCY",
                address="[REDACTED]",
                city=city,
                state="California",
                zip_code="XXXXX",
                make=make,
                year_model=year,
                class_type="UNDERCOVER",
                type_license="Special",
                expiration_date=fake.date_between(start_date=date.today(), end_date=date.today() + timedelta(days=365)),
                amount_paid=0.00,  # Often no fee for government vehicles
                approval_status="pending",
                active_status=True
            )
            db.add(undercover)
        
        # Every 15th record, create a fictitious version
        if i % 15 == 0:
            fictitious = VehicleRegistrationFictitious(
                master_record_id=None,  # Will be set after master is saved
                license_number="FAKE" + str(random.randint(100, 999)),
                vehicle_id_number="TEST" + generate_vin()[:13],
                registered_owner="TEST USER " + str(i),
                address=fake.street_address(),
                city=city,
                state="California",
                zip_code=fake.zipcode_in_state("CA"),
                make=make,
                model="TEST " + model,
                year_model=year,
                vlp_class="FICTITIOUS",
                amount_due=100.00,
                amount_received=0.00,
                approval_status="pending",
                active_status=True
            )
            db.add(fictitious)
    
    db.commit()
    print(f"✅ Created {count} vehicle registration records with undercover and fictitious variants")

def populate_sample_data(db: Session):
    """Populate database with sample data"""
    print("🚀 Starting sample data generation...")
    
    create_action_types(db)
    create_vehicle_registration_samples(db, 100)
    
    print("✅ Sample data generation completed!")
