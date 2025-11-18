"""
Script to populate all Vehicle Registration tables with sample data.
Run this from project root: python -m scripts.populate_vr_tables
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.vehicle_registration import (
    VehicleRegistrationMaster,
    VehicleRegistrationUnderCover,
    VehicleRegistrationFictitious,
    VehicleRegistrationContact,
    VehicleRegistrationReciprocalIssued,
    VehicleRegistrationReciprocalReceived,
    VehicleRegistrationUnderCoverTrapInfo,
    VehicleRegistrationFictitiousTrapInfo
)


def clear_all_vr_tables(db: Session):
    """Clear all VR tables in reverse dependency order"""
    print("Clearing existing VR data...")
    
    # Clear dependent tables first
    db.query(VehicleRegistrationUnderCoverTrapInfo).delete()
    db.query(VehicleRegistrationFictitiousTrapInfo).delete()
    db.query(VehicleRegistrationContact).delete()
    db.query(VehicleRegistrationReciprocalIssued).delete()
    db.query(VehicleRegistrationReciprocalReceived).delete()
    db.query(VehicleRegistrationUnderCover).delete()
    db.query(VehicleRegistrationFictitious).delete()
    
    # Clear master table last
    db.query(VehicleRegistrationMaster).delete()
    
    db.commit()
    print("✓ All VR tables cleared")


def populate_master_records(db: Session):
    """Populate master vehicle registration records"""
    print("\nPopulating Master records...")
    
    masters = [
        VehicleRegistrationMaster(
            license_number="AQC123",
            vehicle_id_number="1HGCM82633A123456",
            registered_owner="John Doe",
            address="123 Main St",
            city="Los Angeles",
            state="California",
            zip_code="90001",
            make="Honda",
            model="Accord",
            year_model=2020,
            year_sold=2020,
            body_type="Sedan",
            type_license="Passenger",
            type_vehicle="Car",
            category="Personal",
            expiration_date=date.today() + timedelta(days=365),
            date_issued=date.today() - timedelta(days=100),
            date_received=date.today() - timedelta(days=95),
            date_fee_received=date.today() - timedelta(days=90),
            amount_paid=Decimal("350.00"),
            use_tax=Decimal("25.00"),
            sticker_issued="Yes",
            sticker_numbers="ST-001",
            paper_issue_code="P001",
            years_renewed=1,
            approval_status="approved",
            active_status=True,
            record_type="master",
            description="Standard registration",
            cert_type="Standard",
            mp="180HP",
            mo="ACC-2020",
            axl="2",
            wc="Class 1",
            cc_alco="1998cc"
        ),
        VehicleRegistrationMaster(
            license_number="XQZ789",
            vehicle_id_number="5YFBURHE1HP654321",
            registered_owner="Jane Smith",
            address="456 Oak Ave",
            city="San Francisco",
            state="California",
            zip_code="94102",
            make="Toyota",
            model="Corolla",
            year_model=2021,
            year_sold=2021,
            body_type="Sedan",
            type_license="Passenger",
            type_vehicle="Car",
            category="Personal",
            expiration_date=date.today() + timedelta(days=300),
            date_issued=date.today() - timedelta(days=80),
            date_received=date.today() - timedelta(days=75),
            date_fee_received=date.today() - timedelta(days=70),
            amount_paid=Decimal("320.00"),
            use_tax=Decimal("22.00"),
            sticker_issued="Yes",
            sticker_numbers="ST-002",
            paper_issue_code="P002",
            years_renewed=0,
            approval_status="pending",
            active_status=True,
            record_type="master",
            description="New registration"
        ),
        VehicleRegistrationMaster(
            license_number="LQN456",
            vehicle_id_number="1G1YY22G065789012",
            registered_owner="Bob Johnson",
            address="789 Pine Rd",
            city="San Diego",
            state="California",
            zip_code="92101",
            make="Chevrolet",
            model="Corvette",
            year_model=2019,
            year_sold=2019,
            body_type="Coupe",
            type_license="Passenger",
            type_vehicle="Sports Car",
            category="Personal",
            expiration_date=date.today() + timedelta(days=200),
            date_issued=date.today() - timedelta(days=150),
            date_received=date.today() - timedelta(days=145),
            date_fee_received=date.today() - timedelta(days=140),
            amount_paid=Decimal("450.00"),
            use_tax=Decimal("35.00"),
            sticker_issued="Yes",
            sticker_numbers="ST-003",
            paper_issue_code="P003",
            years_renewed=2,
            approval_status="approved",
            active_status=True,
            record_type="master"
        )
    ]
    
    db.add_all(masters)
    db.commit()
    
    for master in masters:
        db.refresh(master)
    
    print(f"✓ Added {len(masters)} master records")
    return masters


def populate_contacts(db: Session, masters):
    """Populate contact records"""
    print("\nPopulating Contact records...")
    
    contacts = [
        VehicleRegistrationContact(
            master_record_id=masters[0].id,
            contact_name="John Doe",
            department="Personal",
            email="john.doe@email.com",
            phone_number="555-0101",
            alt_contact_1="Jane Doe: 555-0102",
            alt_contact_2="Jim Doe: 555-0103"
        ),
        VehicleRegistrationContact(
            master_record_id=masters[1].id,
            contact_name="Jane Smith",
            department="Personal",
            email="jane.smith@email.com",
            phone_number="555-0201",
            alt_contact_1="John Smith: 555-0202"
        ),
        VehicleRegistrationContact(
            master_record_id=masters[2].id,
            contact_name="Bob Johnson",
            department="Personal",
            email="bob.johnson@email.com",
            phone_number="555-0301"
        )
    ]
    
    db.add_all(contacts)
    db.commit()
    print(f"✓ Added {len(contacts)} contact records")


def populate_undercover_records(db: Session, masters):
    """Populate undercover vehicle records"""
    print("\nPopulating UnderCover records...")
    
    undercovers = [
        VehicleRegistrationUnderCover(
            master_record_id=masters[0].id,
            license_number="UC001",
            vehicle_id_number="UC1234567890",
            registered_owner="UC Agency Alpha",
            address="Secret Location A",
            city="Los Angeles",
            state="California",
            zip_code="90001",
            make="Ford",
            model="Explorer",
            year_model=2022,
            class_type="SUV",
            type_license="Government",
            body_type="SUV",
            type_vehicle="Utility",
            category="Law Enforcement",
            expiration_date=date.today() + timedelta(days=365),
            date_issued=date.today() - timedelta(days=50),
            date_received=date.today() - timedelta(days=45),
            date_fee_received=date.today() - timedelta(days=40),
            amount_paid=Decimal("0.00"),
            use_tax=Decimal("0.00"),
            sticker_issued="No",
            sticker_numbers="UC-ST-001",
            active_status=True,
            description="Undercover surveillance vehicle"
        ),
        VehicleRegistrationUnderCover(
            master_record_id=masters[1].id,
            license_number="UC002",
            vehicle_id_number="UC0987654321",
            registered_owner="UC Agency Beta",
            address="Secret Location B",
            city="San Francisco",
            state="California",
            zip_code="94102",
            make="Dodge",
            model="Charger",
            year_model=2021,
            class_type="Sedan",
            type_license="Government",
            body_type="Sedan",
            type_vehicle="Car",
            category="Law Enforcement",
            expiration_date=date.today() + timedelta(days=300),
            date_issued=date.today() - timedelta(days=60),
            date_received=date.today() - timedelta(days=55),
            date_fee_received=date.today() - timedelta(days=50),
            amount_paid=Decimal("0.00"),
            use_tax=Decimal("0.00"),
            sticker_issued="No",
            sticker_numbers="UC-ST-002",
            active_status=True,
            description="Undercover pursuit vehicle"
        )
    ]
    
    db.add_all(undercovers)
    db.commit()
    
    for uc in undercovers:
        db.refresh(uc)
    
    print(f"✓ Added {len(undercovers)} undercover records")
    return undercovers


def populate_undercover_trap_info(db: Session, undercovers):
    """Populate undercover trap info"""
    print("\nPopulating UnderCover Trap Info...")
    
    trap_infos = [
        VehicleRegistrationUnderCoverTrapInfo(
            undercover_id=undercovers[0].id,
            date=date.today() - timedelta(days=30),
            number="TRAP-UC-001"
        ),
        VehicleRegistrationUnderCoverTrapInfo(
            undercover_id=undercovers[0].id,
            date=date.today() - timedelta(days=15),
            number="TRAP-UC-002"
        ),
        VehicleRegistrationUnderCoverTrapInfo(
            undercover_id=undercovers[1].id,
            date=date.today() - timedelta(days=20),
            number="TRAP-UC-003"
        )
    ]
    
    db.add_all(trap_infos)
    db.commit()
    print(f"✓ Added {len(trap_infos)} undercover trap info records")


def populate_fictitious_records(db: Session, masters):
    """Populate fictitious vehicle records"""
    print("\nPopulating Fictitious records...")
    
    fictitious = [
        VehicleRegistrationFictitious(
            master_record_id=masters[0].id,
            license_number="FC001",
            vehicle_id_number="FC1234567890",
            registered_owner="Fictitious Corp A",
            address="PO Box 100",
            city="Los Angeles",
            state="California",
            zip_code="90001",
            make="Generic",
            model="Model X",
            year_model=2020,
            vlp_class="Commercial",
            body_type="Van",
            type_license="Commercial",
            type_vehicle="Van",
            category="Business",
            date_issued=date.today() - timedelta(days=100),
            expiration_date=date.today() + timedelta(days=265),
            date_fee_received=date.today() - timedelta(days=95),
            amount_paid=Decimal("500.00"),
            amount_due=Decimal("0.00"),
            amount_received=Decimal("500.00"),
            use_tax=Decimal("40.00"),
            sticker_issued="Yes",
            sticker_numbers="FC-ST-001",
            active_status=True,
            description="Fictitious business vehicle"
        ),
        VehicleRegistrationFictitious(
            master_record_id=masters[2].id,
            license_number="FC002",
            vehicle_id_number="FC0987654321",
            registered_owner="Fictitious Corp B",
            address="PO Box 200",
            city="San Diego",
            state="California",
            zip_code="92101",
            make="Brand",
            model="Model Y",
            year_model=2021,
            vlp_class="Commercial",
            body_type="Truck",
            type_license="Commercial",
            type_vehicle="Truck",
            category="Business",
            date_issued=date.today() - timedelta(days=80),
            expiration_date=date.today() + timedelta(days=285),
            date_fee_received=date.today() - timedelta(days=75),
            amount_paid=Decimal("600.00"),
            amount_due=Decimal("100.00"),
            amount_received=Decimal("500.00"),
            use_tax=Decimal("50.00"),
            sticker_issued="Pending",
            sticker_numbers="FC-ST-002",
            active_status=True,
            description="Fictitious commercial truck"
        )
    ]
    
    db.add_all(fictitious)
    db.commit()
    
    for fc in fictitious:
        db.refresh(fc)
    
    print(f"✓ Added {len(fictitious)} fictitious records")
    return fictitious


def populate_fictitious_trap_info(db: Session, fictitious):
    """Populate fictitious trap info"""
    print("\nPopulating Fictitious Trap Info...")
    
    trap_infos = [
        VehicleRegistrationFictitiousTrapInfo(
            fictitious_id=fictitious[0].id,
            date=date.today() - timedelta(days=25),
            number="TRAP-FC-001"
        ),
        VehicleRegistrationFictitiousTrapInfo(
            fictitious_id=fictitious[1].id,
            date=date.today() - timedelta(days=10),
            number="TRAP-FC-002"
        )
    ]
    
    db.add_all(trap_infos)
    db.commit()
    print(f"✓ Added {len(trap_infos)} fictitious trap info records")


def populate_reciprocal_issued(db: Session, masters):
    """Populate reciprocal issued records"""
    print("\nPopulating Reciprocal Issued records...")
    
    reciprocals = [
        VehicleRegistrationReciprocalIssued(
            master_record_id=masters[0].id,
            description="Reciprocal agreement with Nevada",
            license_plate="NV-ABC123",
            state="Nevada",
            year_of_renewal=2024,
            cancellation_date=None,
            sticker_number="RI-001"
        ),
        VehicleRegistrationReciprocalIssued(
            master_record_id=masters[1].id,
            description="Reciprocal agreement with Arizona",
            license_plate="AZ-XYZ789",
            state="Arizona",
            year_of_renewal=2024,
            cancellation_date=None,
            sticker_number="RI-002"
        )
    ]
    
    db.add_all(reciprocals)
    db.commit()
    print(f"✓ Added {len(reciprocals)} reciprocal issued records")


def populate_reciprocal_received(db: Session, masters):
    """Populate reciprocal received records"""
    print("\nPopulating Reciprocal Received records...")
    
    reciprocals = [
        VehicleRegistrationReciprocalReceived(
            master_record_id=masters[1].id,
            description="Received from Oregon",
            license_plate="OR-LMN456",
            state="Oregon",
            year_of_renewal=2024,
            cancellation_date=None,
            sticker_number="RR-001"
        ),
        VehicleRegistrationReciprocalReceived(
            master_record_id=masters[2].id,
            description="Received from Washington",
            license_plate="WA-RST012",
            state="Washington",
            year_of_renewal=2023,
            cancellation_date=date.today() - timedelta(days=30),
            sticker_number="RR-002"
        )
    ]
    
    db.add_all(reciprocals)
    db.commit()
    print(f"✓ Added {len(reciprocals)} reciprocal received records")


def main():
    """Main function to populate all VR tables"""
    print("="*60)
    print("Vehicle Registration Tables Population Script")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_all_vr_tables(db)
        
        # Populate tables in dependency order
        masters = populate_master_records(db)
        populate_contacts(db, masters)
        undercovers = populate_undercover_records(db, masters)
        populate_undercover_trap_info(db, undercovers)
        fictitious = populate_fictitious_records(db, masters)
        populate_fictitious_trap_info(db, fictitious)
        populate_reciprocal_issued(db, masters)
        populate_reciprocal_received(db, masters)
        
        print("\n" + "="*60)
        print("✓ All VR tables populated successfully!")
        print("="*60)
        
        # Print summary
        print("\nSummary:")
        print(f"  Master Records: {db.query(VehicleRegistrationMaster).count()}")
        print(f"  Contacts: {db.query(VehicleRegistrationContact).count()}")
        print(f"  UnderCover Records: {db.query(VehicleRegistrationUnderCover).count()}")
        print(f"  UnderCover Trap Info: {db.query(VehicleRegistrationUnderCoverTrapInfo).count()}")
        print(f"  Fictitious Records: {db.query(VehicleRegistrationFictitious).count()}")
        print(f"  Fictitious Trap Info: {db.query(VehicleRegistrationFictitiousTrapInfo).count()}")
        print(f"  Reciprocal Issued: {db.query(VehicleRegistrationReciprocalIssued).count()}")
        print(f"  Reciprocal Received: {db.query(VehicleRegistrationReciprocalReceived).count()}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
