"""
Creates a test_table in PostgreSQL, inserts one row, fetches it, and prints the result.
Demonstrates basic SQLAlchemy usage for table creation, insert, and select operations.
"""
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://admin:admin123@localhost:5432/fiverr_db")

with engine.connect() as conn:
    # 1. Create table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        )
    """))
    conn.commit()

    # 2. Insert one row
    conn.execute(text("INSERT INTO test_table (name) VALUES ('Test User')"))
    conn.commit()

    # 3. Fetch and print the row
    result = conn.execute(text("SELECT id, name FROM test_table ORDER BY id DESC LIMIT 1"))
    row = result.fetchone()
    print(f"ID: {row[0]}, Name: {row[1]}")
