from sqlalchemy import inspect
from app.database import engine

def debug_schema():
    inspector = inspect(engine)
    print("Tables in database:")
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        if table_name in ["modules", "permissions"]:
            print(f"  Columns in {table_name}:")
            for column in inspector.get_columns(table_name):
                print(f"    - {column['name']} ({column['type']})")

if __name__ == "__main__":
    debug_schema()
