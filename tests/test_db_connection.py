"""
Pytest tests for database connectivity and table creation.
Updated to verify supplier module tables and relationships.
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
    """Verifies the toys table exists and has the expected structure including supplier_id."""
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
    assert "supplier_id" in columns
    # in_stock has default true (PostgreSQL may store as "true" or "((true))")
    assert columns["in_stock"][3] is not None
    # supplier_id should be nullable
    assert columns["supplier_id"][2] == "YES"


def test_suppliers_table_exists():
    """Verifies the suppliers table exists and has the expected structure."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'suppliers'
                ORDER BY ordinal_position
            """)
        )
        columns = {row[0]: row for row in result.fetchall()}

    assert "id" in columns
    assert "name" in columns
    assert "email" in columns
    assert "specialty" in columns
    # All fields except id should be NOT NULL
    assert columns["name"][2] == "NO"
    assert columns["email"][2] == "NO"
    assert columns["specialty"][2] == "NO"


def test_foreign_key_constraint_exists():
    """Verifies the foreign key constraint between toys and suppliers exists."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT constraint_name, table_name, column_name
                FROM information_schema.key_column_usage
                WHERE table_name = 'toys' AND column_name = 'supplier_id'
            """)
        )
        constraints = result.fetchall()
    
    # Should have at least one constraint on supplier_id
    assert len(constraints) > 0


def test_critical_inventory_view_exists():
    """Verifies the critical_inventory_view exists."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT table_name
                FROM information_schema.views
                WHERE table_name = 'critical_inventory_view'
            """)
        )
        views = result.fetchall()
    
    assert len(views) == 1

