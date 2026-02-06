"""
Cleans all test data from the database.
Useful for manual cleanup between test runs or development.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.database import engine

print("Cleaning test data from database...")

with engine.connect() as conn:
    # Delete toys first (foreign key constraint)
    result = conn.execute(text("DELETE FROM toys RETURNING id"))
    toy_count = len(result.fetchall())
    
    # Delete suppliers
    result = conn.execute(text("DELETE FROM suppliers RETURNING id"))
    supplier_count = len(result.fetchall())
    
    conn.commit()
    
    print(f"✓ Deleted {toy_count} toy(s)")
    print(f"✓ Deleted {supplier_count} supplier(s)")
    print("\n✅ Database cleaned successfully!")
