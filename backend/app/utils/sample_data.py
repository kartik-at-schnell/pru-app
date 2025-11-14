from faker import Faker
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random
from app.models import (
    VehicleRegistrationMaster,
    VehicleRegistrationUnderCover,
    VehicleRegistrationFictitious,
    VehicleRegistrationContact,
    VehicleRegistrationUnderCoverTrapInfo,
    VehicleRegistrationFictitiousTrapInfo,
    VehicleRegistrationReciprocalIssued,
    VehicleRegistrationReciprocalReceived
)

fake = Faker('en_US')

# ============================================================================
# CALIFORNIA-SPECIFIC DATA
# ============================================================================

CALIFORNIA_CITIES = [
    "Los Angeles", "San Francisco", "San Diego", "Sacramento", "Oakland",
    "Fresno", "Long Beach", "Santa Ana", "Anaheim", "Riverside",
    "Bakersfield", "Stockton", "Chula Vista", "Fremont", "San Jose",
    "Berkeley", "Pasadena", "Irvine", "Santa Monica", "Venice"
]

CAR_MAKES = [
    "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz",
    "Audi", "Volkswagen", "Hyundai", "Kia", "Subaru", "Mazda", "Lexus", "Tesla"
]

LICENSE_PLATE_FORMATS = [
    "ABC1234", "AB12345", "A1234BC", "1ABC2345"
]

DEPARTMENTS = [
    "DMV", "CHP", "NHTSA", "FBI", "Local Police", "Highway Patrol", 
    "County Sheriff", "Municipal Police"
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_california_license_plate():
    """Generate realistic California license plate"""
    formats = [
        f"{random.randint(1,9)}{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(100,999)}",
        f"{random.randint(10,99)}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(100,999)}",
        f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(1000,9999)}",
    ]
    return random.choice(formats)

def generate_vin():
    """Generate realistic 17-character VIN"""
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"  # No I, O, Q
    return ''.join(random.choice(chars) for _ in range(17))

# ============================================================================
# 1. VEHICLE REGISTRATION MASTER - Main Records
# ============================================================================

def create_vehicle_registration_master(db: Session, count: int = 10):
    """Create Master vehicle registration records"""
    print(f"\n📋 Creating {count} Master Vehicle Registration Records...")
    
    statuses = ["pending"] * 5 + ["approved"] * 3 + ["rejected"] * 2
    random.shuffle(statuses)
    
    generated_vins = set()
    master_ids = []
    
    for i in range(count):
        city = random.choice(CALIFORNIA_CITIES)
        make = random.choice(CAR_MAKES)
        model = fake.word().title() + " " + fake.word().title()
        year = random.randint(2010, 2024)
        
        # Generate unique VIN
        vin = generate_vin()
        while vin in generated_vins:
            vin = generate_vin()
        generated_vins.add(vin)
        
        record = VehicleRegistrationMaster(
            license_number=generate_california_license_plate(),
            vehicle_id_number=vin,
            registered_owner=fake.name(),
            address=fake.street_address(),
            city=city,
            state="California",
            zip_code=fake.zipcode_in_state("CA"),
            make=make,
            model=model,
            year_model=year,
            body_type=random.choice(["Sedan", "SUV", "Truck", "Coupe", "Hatchback"]),
            type_license=random.choice(["Regular", "Commercial", "Motorcycle"]),
            type_vehicle=random.choice(["Passenger", "Commercial", "Motorcycle"]),
            category=random.choice(["Personal", "Business", "Government"]),
            expiration_date=fake.date_between(start_date=date.today(), end_date=date.today() + timedelta(days=365*2)),
            date_issued=fake.date_between(start_date=date.today() - timedelta(days=365), end_date=date.today()),
            date_fee_received=fake.date_between(start_date=date.today() - timedelta(days=30), end_date=date.today()),
            amount_paid=round(random.uniform(100.0, 500.0), 2),
            use_tax=round(random.uniform(0.0, 50.0), 2),
            sticker_issued=f"ST{random.randint(100000, 999999)}",
            sticker_numbers=f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            approval_status=statuses[i % len(statuses)],
            active_status=True,
            record_type="master",
            description=f"Vehicle registration for {make} {model} {year}"
        )
        
        db.add(record)
        db.flush()  # Flush to get auto-generated ID
        master_ids.append(record.id)
    
    db.commit()
    print(f"✅ Created {count} Master records (IDs: {master_ids[0]}-{master_ids[-1]})")
    return master_ids

# ============================================================================
# 2. VEHICLE REGISTRATION UNDERCOVER
# ============================================================================

def create_undercover_records(db: Session, master_ids: list):
    """Create Undercover vehicle registration records"""
    print(f"\n📋 Creating Undercover Vehicle Registration Records...")
    
    undercover_ids = []
    generated_vins = set()
    
    for idx, master_id in enumerate(master_ids[:5]):  # Create for first 5 masters
        city = random.choice(CALIFORNIA_CITIES)
        make = random.choice(CAR_MAKES)
        year = random.randint(2010, 2024)
        
        vin = generate_vin()
        while vin in generated_vins:
            vin = generate_vin()
        generated_vins.add(vin)
        
        undercover = VehicleRegistrationUnderCover(
            master_record_id=master_id,  # Reference to master (NOT FK)
            license_number=generate_california_license_plate(),
            vehicle_id_number=vin,
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
            date_issued=date.today() - timedelta(days=random.randint(30, 365)),
            date_fee_received=date.today() - timedelta(days=random.randint(1, 30)),
            amount_paid=0.00,
            approval_status="approved",
            active_status=True
        )
        
        db.add(undercover)
        db.flush()
        undercover_ids.append(undercover.id)
    
    db.commit()
    print(f"✅ Created {len(undercover_ids)} Undercover records (IDs: {undercover_ids})")
    return undercover_ids

# ============================================================================
# 3. VEHICLE REGISTRATION FICTITIOUS
# ============================================================================

def create_fictitious_records(db: Session, master_ids: list):
    """Create Fictitious vehicle registration records"""
    print(f"\n📋 Creating Fictitious Vehicle Registration Records...")
    
    fictitious_ids = []
    generated_vins = set()
    
    for idx, master_id in enumerate(master_ids[:5]):  # Create for first 5 masters
        city = random.choice(CALIFORNIA_CITIES)
        make = random.choice(CAR_MAKES)
        model = fake.word().title()
        year = random.randint(2010, 2024)
        
        vin = generate_vin()
        while vin in generated_vins:
            vin = generate_vin()
        generated_vins.add(vin)
        
        fictitious = VehicleRegistrationFictitious(
            master_record_id=master_id,  # Reference to master (NOT FK)
            license_number="FAKE" + str(random.randint(100, 999)),
            vehicle_id_number=vin,
            registered_owner=fake.name(),
            address=fake.street_address(),
            city=city,
            state="California",
            zip_code=fake.zipcode_in_state("CA"),
            make=make,
            model=model,
            year_model=year,
            vlp_class="FICTITIOUS",
            amount_due=150.00,
            amount_received=0.00,
            approval_status="pending",
            active_status=True
        )
        
        db.add(fictitious)
        db.flush()
        fictitious_ids.append(fictitious.id)
    
    db.commit()
    print(f"✅ Created {len(fictitious_ids)} Fictitious records (IDs: {fictitious_ids})")
    return fictitious_ids

# ============================================================================
# 4. VEHICLE REGISTRATION CONTACT
# ============================================================================

def create_contacts(db: Session, master_ids: list):
    """Create Contact records for Masters"""
    print(f"\n📋 Creating Contact Records...")
    
    contact_ids = []
    
    for master_id in master_ids[:7]:  # Create for first 7 masters
        for _ in range(random.randint(1, 3)):  # 1-3 contacts per master
            contact = VehicleRegistrationContact(
                master_record_id=master_id,
                contact_name=fake.name(),
                department=random.choice(DEPARTMENTS),
                email=fake.email(),
                phone_number=fake.phone_number()[:20],
                alt_contact_1=fake.name() if random.random() > 0.5 else None,
                alt_contact_2=fake.name() if random.random() > 0.5 else None
            )
            
            db.add(contact)
            db.flush()
            contact_ids.append(contact.id)
    
    db.commit()
    print(f"✅ Created {len(contact_ids)} Contact records (IDs: {contact_ids[:3]}...)")
    return contact_ids

# ============================================================================
# 5. UNDERCOVER TRAP INFO
# ============================================================================

def create_undercover_trap_info(db: Session, undercover_ids: list):
    """Create Trap Info for Undercover records"""
    print(f"\n📋 Creating Undercover Trap Info Records...")
    
    trap_ids = []
    
    for undercover_id in undercover_ids:
        for _ in range(random.randint(1, 3)):  # 1-3 trap infos per undercover
            trap = VehicleRegistrationUnderCoverTrapInfo(
                undercover_id=undercover_id,
                date=fake.date_between(start_date=date.today() - timedelta(days=90), end_date=date.today()),
                number=f"TRAP{random.randint(100000, 999999)}"
            )
            
            db.add(trap)
            db.flush()
            trap_ids.append(trap.id)
    
    db.commit()
    print(f"✅ Created {len(trap_ids)} Undercover Trap Info records (IDs: {trap_ids[:3]}...)")
    return trap_ids

# ============================================================================
# 6. FICTITIOUS TRAP INFO
# ============================================================================

def create_fictitious_trap_info(db: Session, fictitious_ids: list):
    """Create Trap Info for Fictitious records"""
    print(f"\n📋 Creating Fictitious Trap Info Records...")
    
    trap_ids = []
    
    for fictitious_id in fictitious_ids:
        for _ in range(random.randint(1, 2)):  # 1-2 trap infos per fictitious
            trap = VehicleRegistrationFictitiousTrapInfo(
                fictitious_id=fictitious_id,
                date=fake.date_between(start_date=date.today() - timedelta(days=60), end_date=date.today()),
                number=f"FICTRAP{random.randint(100000, 999999)}"
            )
            
            db.add(trap)
            db.flush()
            trap_ids.append(trap.id)
    
    db.commit()
    print(f"✅ Created {len(trap_ids)} Fictitious Trap Info records (IDs: {trap_ids[:3]}...)")
    return trap_ids

# ============================================================================
# 7. RECIPROCAL ISSUED
# ============================================================================

def create_reciprocal_issued(db: Session, master_ids: list):
    """Create Reciprocal Issued records"""
    print(f"\n📋 Creating Reciprocal Issued Records...")
    
    reciprocal_ids = []
    
    for master_id in master_ids[:6]:  # Create for first 6 masters
        for _ in range(random.randint(1, 2)):
            reciprocal = VehicleRegistrationReciprocalIssued(
                master_record_id=master_id,
                description=f"Reciprocal agreement issued for vehicle registration",
                license_plate=generate_california_license_plate(),
                state="California",
                year_of_renewal=random.randint(2024, 2026),
                cancellation_date=None if random.random() > 0.3 else fake.date_between(start_date=date.today(), end_date=date.today() + timedelta(days=365)),
                sticker_number=f"RECP{random.randint(1000000, 9999999)}"
            )
            
            db.add(reciprocal)
            db.flush()
            reciprocal_ids.append(reciprocal.id)
    
    db.commit()
    print(f"✅ Created {len(reciprocal_ids)} Reciprocal Issued records (IDs: {reciprocal_ids[:3]}...)")
    return reciprocal_ids

# ============================================================================
# 8. RECIPROCAL RECEIVED
# ============================================================================

def create_reciprocal_received(db: Session, master_ids: list):
    """Create Reciprocal Received records"""
    print(f"\n📋 Creating Reciprocal Received Records...")
    
    reciprocal_ids = []
    
    for master_id in master_ids[4:9]:  # Create for masters 4-8
        for _ in range(random.randint(1, 2)):
            reciprocal = VehicleRegistrationReciprocalReceived(
                master_record_id=master_id,
                description=f"Reciprocal agreement received for vehicle",
                license_plate=generate_california_license_plate(),
                state=random.choice(["Nevada", "Oregon", "Arizona", "Utah"]),
                year_of_renewal=random.randint(2024, 2026),
                cancellation_date=None if random.random() > 0.5 else fake.date_between(start_date=date.today(), end_date=date.today() + timedelta(days=180)),
                sticker_number=f"RECV{random.randint(1000000, 9999999)}"
            )
            
            db.add(reciprocal)
            db.flush()
            reciprocal_ids.append(reciprocal.id)
    
    db.commit()
    print(f"✅ Created {len(reciprocal_ids)} Reciprocal Received records (IDs: {reciprocal_ids[:3]}...)")
    return reciprocal_ids

# ============================================================================
# MAIN POPULATE FUNCTION
# ============================================================================

def populate_sample_data(db: Session):
    """Populate ALL tables with sample data"""
    print("\n" + "="*80)
    print("🚀 STARTING SAMPLE DATA POPULATION - CALIFORNIA STATE DATA")
    print("="*80)
    
    try:
        # 1. Create Master records
        master_ids = create_vehicle_registration_master(db, count=10)
        
        # 2. Create Undercover records
        undercover_ids = create_undercover_records(db, master_ids)
        
        # 3. Create Fictitious records
        fictitious_ids = create_fictitious_records(db, master_ids)
        
        # 4. Create Contacts
        contact_ids = create_contacts(db, master_ids)
        
        # 5. Create Undercover Trap Info
        uc_trap_ids = create_undercover_trap_info(db, undercover_ids)
        
        # 6. Create Fictitious Trap Info
        fict_trap_ids = create_fictitious_trap_info(db, fictitious_ids)
        
        # 7. Create Reciprocal Issued
        recp_issued_ids = create_reciprocal_issued(db, master_ids)
        
        # 8. Create Reciprocal Received
        recp_received_ids = create_reciprocal_received(db, master_ids)
        
        # Print Summary
        print("\n" + "="*80)
        print("✅ SAMPLE DATA POPULATION COMPLETE!")
        print("="*80)
        print(f"\n📊 SUMMARY:")
        print(f"   • Master Records: {len(master_ids)} (IDs: 1-{len(master_ids)})")
        print(f"   • Undercover Records: {len(undercover_ids)}")
        print(f"   • Fictitious Records: {len(fictitious_ids)}")
        print(f"   • Contact Records: {len(contact_ids)}")
        print(f"   • UC Trap Info: {len(uc_trap_ids)}")
        print(f"   • Fictitious Trap Info: {len(fict_trap_ids)}")
        print(f"   • Reciprocal Issued: {len(recp_issued_ids)}")
        print(f"   • Reciprocal Received: {len(recp_received_ids)}")
        print(f"\n   🎯 All IDs are auto-incrementing integers starting from 0001")
        print(f"   📍 All data is California State specific")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR during population: {e}")
        db.rollback()
        raise