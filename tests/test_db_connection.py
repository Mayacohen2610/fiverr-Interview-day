"""
Pytest tests for database connectivity and table creation.
"""
from sqlalchemy import create_engine, text

from app.database import DATABASE_URL


def test_database_connection():
    """Verifies connection to the PostgreSQL database."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1


def test_toys_table_exists():
    """Verifies the toys table exists and has the expected structure."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'toys'
                ORDER BY ordinal_position
            """)
        )
        columns = {row[0]: row for row in result.fetchall()}

    assert "id" in columns
    assert "toy_name" in columns
    assert "category" in columns
    assert "price" in columns
    assert "in_stock" in columns
    # in_stock has default true (PostgreSQL may store as "true" or "((true))")
    assert columns["in_stock"][3] is not None


def test_create_toys_table_if_not_exists():
    """
    Ensures toys table can be created (idempotent).
    Matches the create_toys_table script logic.
    """
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(
            text("""
                CREATE TABLE IF NOT EXISTS toys (
                    id SERIAL PRIMARY KEY,
                    toy_name VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    in_stock BOOLEAN DEFAULT TRUE
                )
            """)
        )
        conn.commit()