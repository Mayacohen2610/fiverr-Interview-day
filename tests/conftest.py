"""
Pytest configuration and fixtures for test suite.
Provides database cleanup and test isolation.
"""
import pytest
from sqlalchemy import create_engine, text

from app.database import DATABASE_URL


@pytest.fixture(scope="function", autouse=True)
def cleanup_database():
    """
    Fixture that runs before each test function.
    Cleans up all test data to ensure test isolation.
    
    This fixture:
    1. Runs before each test (autouse=True)
    2. Deletes all toys (must be first due to foreign key)
    3. Deletes all suppliers
    4. Ensures each test starts with a clean slate
    """
    engine = create_engine(DATABASE_URL)
    
    # Cleanup before test runs
    with engine.connect() as conn:
        # Delete toys first (foreign key constraint)
        conn.execute(text("DELETE FROM toys"))
        # Then delete suppliers
        conn.execute(text("DELETE FROM suppliers"))
        conn.commit()
    
    # Run the test
    yield
    
    # Cleanup after test completes (optional, but good practice)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM toys"))
        conn.execute(text("DELETE FROM suppliers"))
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    """
    Fixture that runs once at the start of the test session.
    Verifies that required tables exist before running any tests.
    """
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if suppliers table exists
        result = conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'suppliers'
                )
            """)
        )
        suppliers_exists = result.fetchone()[0]
        
        # Check if toys table exists
        result = conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'toys'
                )
            """)
        )
        toys_exists = result.fetchone()[0]
        
        if not suppliers_exists or not toys_exists:
            pytest.exit(
                "Database tables not found. Please run:\n"
                "  python scripts/create_toys_table.py\n"
                "  python scripts/create_suppliers_table.py",
                returncode=1
            )
