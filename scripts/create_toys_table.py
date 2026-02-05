"""
Creates the 'toys' table in the fiverr_db PostgreSQL database.
Run this script once to set up the table before using the toy endpoints.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.database import engine

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS toys (
            id SERIAL PRIMARY KEY,
            toy_name VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            in_stock BOOLEAN DEFAULT TRUE
        )
    """))
    conn.commit()
    print("Toys table created successfully!")
