"""
Simple script to verify the connection to a local PostgreSQL database.
Uses SQLAlchemy to execute SELECT 1 and prints success or the error message.
"""
from sqlalchemy import create_engine, text

try:
    engine = create_engine(
        "postgresql://admin:admin123@localhost:5432/fiverr_db"
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Successfully connected to Postgres!")
except Exception as e:
    print(e)
