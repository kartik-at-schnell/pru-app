from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base
from app.utils.sample_data import populate_sample_data

def main():
    """Populate database with sample data"""
    print("\n" + "="*80)
    print("📊 DATABASE POPULATION")
    print("="*80)
    
    print("\n🔨 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        print("\n🚀 Populating database with sample data...")
        populate_sample_data(db)
        
        print("\n✅ Database population successful!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
        
    finally:
        db.close()

if __name__ == "__main__":
    main()