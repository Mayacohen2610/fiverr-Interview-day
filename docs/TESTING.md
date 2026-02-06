# Testing Guide

Comprehensive guide to running and understanding the test suite.

## 🚀 Quick Start

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/Mac

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_suppliers.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📊 Test Suite Overview

The project includes **31 automated tests** across 5 test files:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_suppliers.py` | 8 | Supplier CRUD operations |
| `test_supplier_validation.py` | 6 | Specialty rule enforcement |
| `test_critical_inventory.py` | 7 | Critical inventory reporting |
| `test_api.py` | 5 | Basic API functionality |
| `test_db_connection.py` | 5 | Database schema verification |

---

## 🧪 Test Files Explained

### 1. `test_suppliers.py` - Supplier CRUD Operations

Tests all supplier management endpoints:

- ✅ Creating suppliers with valid data
- ✅ Email validation (invalid formats rejected)
- ✅ Unique name constraint (duplicates rejected)
- ✅ Retrieving all suppliers
- ✅ Retrieving single supplier by ID
- ✅ Updating supplier information
- ✅ Deleting suppliers (with and without toys)
- ✅ Category normalization

**Example Test:**
```python
def test_create_supplier_with_valid_data():
    """Tests creating a supplier with all valid fields."""
    supplier = {
        "name": "Test Supplier",
        "email": "test@supplier.com",
        "specialty": "Action Figures"
    }
    response = client.post("/suppliers", json=supplier)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Supplier"
```

### 2. `test_supplier_validation.py` - The Specialty Rule

Tests the core business rule: suppliers can only provide toys in their specialty.

- ✅ Creating toy with nonexistent supplier fails
- ✅ Creating toy with mismatched specialty fails
- ✅ Creating toy with matching specialty succeeds
- ✅ Updating toy to mismatched supplier fails
- ✅ Updating toy to matching supplier succeeds
- ✅ Deleting supplier with toys fails

**Example Test:**
```python
def test_create_toy_with_mismatched_specialty_fails():
    """Tests that creating a toy with mismatched specialty fails."""
    # Create Dolls supplier
    supplier = client.post("/suppliers", json={
        "name": "Dolls Supplier",
        "email": "dolls@supplier.com",
        "specialty": "Dolls"
    }).json()
    
    # Try to create Action Figures toy (should fail)
    toy = {
        "toy_name": "Action Figure",
        "category": "Action Figures",
        "price": 29.99,
        "in_stock": True,
        "supplier_id": supplier["id"]
    }
    response = client.post("/toys", json=toy)
    assert response.status_code == 400
    assert "specialty" in response.json()["detail"].lower()
```

### 3. `test_critical_inventory.py` - Reporting

Tests the critical inventory report functionality:

- ✅ Empty report when no critical items
- ✅ Out-of-stock items appear in report
- ✅ High-value items (>200) appear in report
- ✅ Items meeting both criteria show combined reason
- ✅ Normal items don't appear in report
- ✅ Supplier information included in report
- ✅ Edge case: price exactly 200 (not critical)

**Example Test:**
```python
def test_out_of_stock_items_appear_in_report():
    """Tests that out of stock items appear in critical inventory."""
    # Create supplier and out-of-stock toy
    supplier = create_test_supplier("Test Supplier", "test@supplier.com", "Test Category")
    toy = create_test_toy("Out of Stock Toy", "Test Category", 50.0, False, supplier["id"])
    
    # Check report
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["toy_name"] == "Out of Stock Toy"
    assert "out of stock" in items[0]["reason"].lower()
```

### 4. `test_api.py` - Basic API Functionality

Tests core API operations updated for supplier integration:

- ✅ Health endpoint works
- ✅ GET /toys returns list
- ✅ Toy structure includes supplier info
- ✅ Creating toy with supplier succeeds
- ✅ Creating toy without supplier fails
- ✅ Creating toy with nonexistent supplier fails

### 5. `test_db_connection.py` - Database Schema

Tests database connectivity and schema integrity:

- ✅ Database connection works
- ✅ Toys table exists with correct structure
- ✅ Suppliers table exists with correct structure
- ✅ Foreign key constraint exists
- ✅ Critical inventory view exists

---

## 🔧 Test Fixtures and Cleanup

### Automatic Database Cleanup

The test suite uses **pytest fixtures** defined in `tests/conftest.py` to ensure test isolation:

```python
@pytest.fixture(scope="function", autouse=True)
def cleanup_database():
    """
    Automatically cleans database before and after each test.
    Ensures each test starts with a clean slate.
    """
    # Cleanup before test
    # Run test
    # Cleanup after test
```

**Benefits:**
- ✅ Each test runs independently
- ✅ No data pollution between tests
- ✅ Tests can be run in any order
- ✅ Tests can be run multiple times

### How It Works

1. **Before each test:**
   - Deletes all toys (respecting foreign key constraints)
   - Deletes all suppliers

2. **Test runs** with clean database

3. **After each test:**
   - Cleans up again (optional, but good practice)

### Session-Level Verification

```python
@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    """
    Runs once at test session start.
    Verifies required tables exist.
    """
```

If tables don't exist, provides helpful error message:
```
Database tables not found. Please run:
  python scripts/create_toys_table.py
  python scripts/create_suppliers_table.py
```

---

## 🎯 Running Specific Tests

### Run Single Test File

```bash
pytest tests/test_suppliers.py -v
```

### Run Single Test Function

```bash
pytest tests/test_suppliers.py::test_create_supplier_with_valid_data -v
```

### Run Tests Matching Pattern

```bash
# All tests with "supplier" in the name
pytest tests/ -k "supplier" -v

# All tests with "validation" in the name
pytest tests/ -k "validation" -v
```

### Run Tests with Output

```bash
# Show print statements
pytest tests/ -v -s

# Show test setup/teardown
pytest tests/ -v --setup-show
```

---

## 📈 Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest tests/ --cov=app

# HTML report (opens in browser)
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # Mac/Linux
start htmlcov\index.html  # Windows
```

### Expected Coverage

The test suite provides comprehensive coverage:

- **app/routes.py**: ~95% (all endpoints tested)
- **app/crud.py**: ~90% (all CRUD operations tested)
- **app/schemas.py**: 100% (validation tested)
- **app/models.py**: 100% (used in all tests)

---

## 🐛 Debugging Failed Tests

### View Detailed Output

```bash
# Verbose output with full error messages
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x

# Drop into debugger on failure
pytest tests/ --pdb
```

### Common Test Failures

#### 1. Database Connection Error

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Ensure database is running
docker-compose up -d
docker ps  # Verify containers are running
```

#### 2. Table Not Found Error

**Error:** `relation "suppliers" does not exist`

**Solution:**
```bash
# Run migrations
python scripts/create_toys_table.py
python scripts/create_suppliers_table.py
```

#### 3. Fixture Not Working

**Error:** Tests fail with duplicate data errors

**Solution:**
```bash
# Manual cleanup
python scripts/clean_test_data.py

# Verify conftest.py exists
ls tests/conftest.py
```

---

## 🧹 Manual Database Cleanup

If you need to manually clean test data:

```bash
python scripts/clean_test_data.py
```

**Output:**
```
Cleaning test data from database...
✓ Deleted 15 toy(s)
✓ Deleted 8 supplier(s)

✅ Database cleaned successfully!
```

---

## 🔍 Test Best Practices

### Writing New Tests

When adding new tests, follow these patterns:

1. **Use descriptive names:**
   ```python
   def test_create_supplier_with_invalid_email_fails():
       """Tests that invalid email format is rejected."""
   ```

2. **Arrange-Act-Assert pattern:**
   ```python
   def test_example():
       # Arrange: Set up test data
       supplier = {"name": "Test", "email": "test@test.com", "specialty": "Toys"}
       
       # Act: Perform the action
       response = client.post("/suppliers", json=supplier)
       
       # Assert: Verify the result
       assert response.status_code == 200
   ```

3. **Test one thing per test:**
   - Don't combine multiple assertions for different features
   - Keep tests focused and simple

4. **Use helper functions for common operations:**
   ```python
   def create_test_supplier(name, email, specialty):
       """Helper to create a supplier for testing."""
       return client.post("/suppliers", json={
           "name": name,
           "email": email,
           "specialty": specialty
       }).json()
   ```

---

## 📊 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: admin
          POSTGRES_PASSWORD: admin123
          POSTGRES_DB: fiverr_db
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run migrations
        run: |
          python scripts/create_toys_table.py
          python scripts/create_suppliers_table.py
      
      - name: Run tests
        run: pytest tests/ -v --cov=app
```

---

## 🎓 Test Scenarios Covered

### Happy Path
- ✅ Creating suppliers and toys with valid data
- ✅ Retrieving data via GET endpoints
- ✅ Updating existing records
- ✅ Generating reports

### Error Handling
- ✅ Invalid email formats
- ✅ Duplicate supplier names
- ✅ Nonexistent references (404s)
- ✅ Business rule violations (specialty mismatch)
- ✅ Foreign key constraints (delete with toys)

### Edge Cases
- ✅ Empty databases
- ✅ Boundary values (price exactly 200)
- ✅ NULL supplier_id for toys
- ✅ Category normalization ("plush" → "Plush")

### Integration
- ✅ End-to-end workflows (create supplier → create toy → generate report)
- ✅ Database triggers
- ✅ Database views
- ✅ Foreign key cascades

---

## 📚 Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **FastAPI testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Coverage.py**: https://coverage.readthedocs.io/

---

## ✅ Test Checklist

Before committing code, ensure:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] No new linter errors: Check your IDE
- [ ] Coverage remains high: `pytest tests/ --cov=app`
- [ ] New features have tests
- [ ] Tests are documented with docstrings
- [ ] Database cleanup works properly
