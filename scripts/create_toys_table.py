"""
Creates the 'toys' table in the fiverr_db PostgreSQL database.
Run this script once to set up the table before using the toy endpoints.
"""
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
