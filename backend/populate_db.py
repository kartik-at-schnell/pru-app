# this is also vibe-coded
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base
from app.utils.sample_data import populate_sample_data

def main():
    """Populate database with sample data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        populate_sample_data(db)
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
    print("🎉 Database populated successfully!")

if __name__ == "__main__":
    main()
