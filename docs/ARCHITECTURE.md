# Architecture & Implementation Details

Technical documentation for developers and maintainers.

## 📐 System Architecture

### High-Level Overview

```
┌─────────────┐
│   Client    │
│  (Browser/  │
│   curl)     │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌─────────────────────────────┐   │
│  │  Routes (routes.py)         │   │
│  │  - HTTP handling            │   │
│  │  - Error responses          │   │
│  └────────────┬────────────────┘   │
│               │                     │
│  ┌────────────▼────────────────┐   │
│  │  CRUD (crud.py)             │   │
│  │  - Business logic           │   │
│  │  - SQL operations           │   │
│  │  - Validation               │   │
│  └────────────┬────────────────┘   │
│               │                     │
│  ┌────────────▼────────────────┐   │
│  │  Models (models.py)         │   │
│  │  - SQLAlchemy ORM           │   │
│  │  - Table definitions        │   │
│  └────────────┬────────────────┘   │
└───────────────┼─────────────────────┘
                │ SQL
                ▼
┌─────────────────────────────────────┐
│       PostgreSQL Database           │
│  ┌─────────────────────────────┐   │
│  │  Tables                     │   │
│  │  - suppliers                │   │
│  │  - toys                     │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  Constraints                │   │
│  │  - Foreign keys             │   │
│  │  - Unique constraints       │   │
│  │  - CHECK constraints        │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  Triggers                   │   │
│  │  - validate_supplier_       │   │
│  │    specialty_trigger        │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │  Views                      │   │
│  │  - critical_inventory_view  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### Tables

#### `suppliers` Table
```sql
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL 
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    specialty VARCHAR(255) NOT NULL
);
```

**Constraints:**
- `PRIMARY KEY` on `id` - Auto-incrementing unique identifier
- `UNIQUE` on `name` - No duplicate supplier names
- `CHECK` on `email` - Regex validation for email format
- `NOT NULL` on all columns except `id`

#### `toys` Table
```sql
CREATE TABLE toys (
    id SERIAL PRIMARY KEY,
    toy_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    in_stock BOOLEAN DEFAULT TRUE NOT NULL,
    supplier_id INTEGER,
    CONSTRAINT fk_toys_supplier 
        FOREIGN KEY (supplier_id) 
        REFERENCES suppliers(id) 
        ON DELETE RESTRICT
);
```

**Constraints:**
- `PRIMARY KEY` on `id`
- `FOREIGN KEY` on `supplier_id` → `suppliers(id)`
- `ON DELETE RESTRICT` - Cannot delete supplier with toys
- `supplier_id` is `NULLABLE` for migration purposes

### Database Trigger

#### `validate_supplier_specialty_trigger`

**Purpose:** Enforce the "Specialty Rule" at database level

**Function:**
```sql
CREATE OR REPLACE FUNCTION validate_supplier_specialty()
RETURNS TRIGGER AS $$
DECLARE
    supplier_specialty VARCHAR(255);
BEGIN
    IF NEW.supplier_id IS NOT NULL THEN
        SELECT specialty INTO supplier_specialty 
        FROM suppliers 
        WHERE id = NEW.supplier_id;
        
        IF supplier_specialty IS NULL THEN
            RAISE EXCEPTION 'Supplier with id % does not exist', NEW.supplier_id;
        END IF;
        
        IF supplier_specialty != NEW.category THEN
            RAISE EXCEPTION 
                'Supplier specialty "%" does not match toy category "%". ' ||
                'A supplier can only provide toys in their specialty category.',
                supplier_specialty, NEW.category;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Trigger:**
```sql
CREATE TRIGGER validate_supplier_specialty_trigger
BEFORE INSERT OR UPDATE ON toys
FOR EACH ROW
EXECUTE FUNCTION validate_supplier_specialty();
```

**When it fires:**
- Before INSERT on `toys`
- Before UPDATE on `toys`
- Only if `supplier_id` is not NULL

### Database View

#### `critical_inventory_view`

**Purpose:** Pre-calculated report of critical items

```sql
CREATE VIEW critical_inventory_view AS
SELECT 
    t.id,
    t.toy_name,
    t.category,
    t.price,
    t.in_stock,
    s.name as supplier_name,
    s.email as supplier_email,
    CASE 
        WHEN NOT t.in_stock AND t.price > 200 
            THEN 'Out of stock, High-value item (>200)'
        WHEN NOT t.in_stock 
            THEN 'Out of stock'
        WHEN t.price > 200 
            THEN 'High-value item (>200)'
    END as reason
FROM toys t
LEFT JOIN suppliers s ON t.supplier_id = s.id
WHERE NOT t.in_stock OR t.price > 200
ORDER BY t.in_stock ASC, t.price DESC;
```

**Logic:**
- `LEFT JOIN` to include toys even without suppliers
- Filter: `NOT in_stock OR price > 200`
- Order: Out of stock first, then by price descending

---

## 🏗️ Application Structure

### File Organization

```
fiverr-Interview-day/
├── app/
│   ├── __init__.py           # Package marker
│   ├── database.py           # DB connection & session
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic schemas
│   ├── crud.py               # Database operations
│   └── routes.py             # API endpoints
├── scripts/
│   ├── create_toys_table.py
│   ├── create_suppliers_table.py
│   ├── seed_suppliers.py
│   └── clean_test_data.py
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   ├── test_api.py
│   ├── test_suppliers.py
│   ├── test_supplier_validation.py
│   ├── test_critical_inventory.py
│   └── test_db_connection.py
├── docs/                     # Documentation
├── main.py                   # Application entry point
├── docker-compose.yml        # Database setup
└── requirements.txt          # Dependencies
```

### Layer Responsibilities

#### 1. Routes Layer (`app/routes.py`)
**Responsibilities:**
- HTTP request/response handling
- Input validation (Pydantic)
- Error handling and status codes
- Dependency injection (database sessions)

**Does NOT:**
- Contain business logic
- Execute SQL directly
- Handle database sessions

**Example:**
```python
@router.post("/suppliers")
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_supplier(db, supplier)
    except IntegrityError as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="Duplicate name")
        raise HTTPException(status_code=400, detail="Failed to create")
```

#### 2. CRUD Layer (`app/crud.py`)
**Responsibilities:**
- Business logic implementation
- SQL query execution
- Application-level validation
- Data transformation

**Does NOT:**
- Handle HTTP requests/responses
- Manage database connections (uses injected sessions)

**Example:**
```python
def create_toy(db: Session, toy: schemas.ToyCreate) -> dict:
    # Application-level validation
    result = db.execute(
        text("SELECT specialty FROM suppliers WHERE id = :supplier_id"),
        {"supplier_id": toy.supplier_id}
    )
    row = result.fetchone()
    if row is None:
        raise ValueError(f"Supplier with id {toy.supplier_id} does not exist")
    
    if row[0] != toy.category:
        raise ValueError(f"Specialty mismatch")
    
    # Execute insert
    # ...
```

#### 3. Models Layer (`app/models.py`)
**Responsibilities:**
- Define database table structure
- Define relationships between tables
- ORM mapping

**Example:**
```python
class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=False)
    
    toys = relationship("Toy", back_populates="supplier")
```

#### 4. Schemas Layer (`app/schemas.py`)
**Responsibilities:**
- Define API request/response contracts
- Input validation
- Data serialization
- Type conversion

**Example:**
```python
class SupplierCreate(BaseModel):
    name: str
    email: EmailStr  # Automatic email validation
    specialty: NormalizedCategory  # Automatic normalization
```

---

## 🔒 Validation Strategy

### Two-Layer Validation

The system implements validation at two levels for maximum data integrity:

#### Layer 1: Application Level (Fast, User-Friendly)

**Location:** `app/crud.py`, `app/schemas.py`

**Advantages:**
- Fast feedback (no database round-trip for some validations)
- User-friendly error messages
- Can provide context-specific errors

**Example:**
```python
# In crud.py
if supplier_specialty != toy.category:
    raise ValueError(
        f'Supplier specialty "{supplier_specialty}" does not match '
        f'toy category "{toy.category}". A supplier can only provide '
        f'toys in their specialty category.'
    )
```

#### Layer 2: Database Level (Safety Net)

**Location:** PostgreSQL trigger

**Advantages:**
- Protects against direct SQL access
- Ensures data integrity even if application is bypassed
- Cannot be circumvented

**Example:**
```sql
-- Trigger fires before INSERT/UPDATE
IF supplier_specialty != NEW.category THEN
    RAISE EXCEPTION 'Supplier specialty "%" does not match toy category "%"',
        supplier_specialty, NEW.category;
END IF;
```

### Validation Types

| Validation | Application | Database | Pydantic |
|------------|-------------|----------|----------|
| Email format | ✅ | ✅ | ✅ |
| Unique supplier name | ❌ | ✅ | ❌ |
| Supplier exists | ✅ | ✅ (FK) | ❌ |
| Specialty matches | ✅ | ✅ | ❌ |
| Category normalization | ✅ | ❌ | ✅ |
| Required fields | ✅ | ✅ | ✅ |

---

## 🎯 Design Decisions

### 1. Nullable `supplier_id`

**Decision:** Make `supplier_id` nullable in `toys` table

**Rationale:**
- Allows gradual migration of existing toys
- No data loss during migration
- New toys still require supplier (enforced at application level)

**Trade-off:**
- Slightly weaker data integrity
- Need to handle NULL in queries (use LEFT JOIN)

### 2. ON DELETE RESTRICT

**Decision:** Use `ON DELETE RESTRICT` for foreign key

**Rationale:**
- Prevents accidental data loss
- Forces explicit reassignment of toys
- Makes deletion intent clear

**Alternative considered:**
- `ON DELETE SET NULL` - Would orphan toys
- `ON DELETE CASCADE` - Would delete toys (data loss)

### 3. Database View for Reports

**Decision:** Use PostgreSQL VIEW instead of application logic

**Rationale:**
- Always up-to-date (no caching issues)
- Efficient SQL execution
- Can be queried directly from database
- Reduces application complexity

**Trade-off:**
- Less flexible than application logic
- Requires database migration to change

### 4. Category Normalization

**Decision:** Normalize all categories to Title Case

**Rationale:**
- Ensures matching works correctly
- User-friendly display
- Prevents "action figures" ≠ "Action Figures" issues

**Implementation:**
```python
def normalize_category_value(value: str) -> str:
    return value.strip().title()

NormalizedCategory = Annotated[str, BeforeValidator(normalize_category_value)]
```

### 5. Error Status Codes

**Decision:** Use specific HTTP status codes

**Mapping:**
- `400 Bad Request` - Validation failures, business rule violations
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Unique constraint violations, delete restrictions
- `422 Unprocessable Entity` - Pydantic validation errors

**Rationale:**
- RESTful best practices
- Clear semantics for clients
- Easy to handle in frontend

---

## 🔄 Data Flow

### Creating a Toy (Happy Path)

```
1. Client sends POST /toys
   {
     "toy_name": "Action Figure",
     "category": "Action Figures",
     "price": 29.99,
     "supplier_id": 1
   }

2. FastAPI receives request
   ↓
3. Pydantic validates schema (ToyCreate)
   - Normalizes category to "Action Figures"
   - Validates price is float
   - Validates supplier_id is int
   ↓
4. Routes layer calls crud.create_toy()
   ↓
5. CRUD layer validates:
   - Supplier exists (SELECT from suppliers)
   - Specialty matches category
   ↓
6. CRUD executes INSERT INTO toys
   ↓
7. Database trigger validates again
   ↓
8. Database returns new row with id
   ↓
9. CRUD returns dict to routes
   ↓
10. Routes returns JSON response
    {
      "id": 5,
      "toy_name": "Action Figure",
      "category": "Action Figures",
      "price": 29.99,
      "in_stock": true,
      "supplier_id": 1
    }
```

### Creating a Toy (Error Path - Specialty Mismatch)

```
1. Client sends POST /toys
   {
     "toy_name": "Doll",
     "category": "Dolls",
     "supplier_id": 1  // Action Figures supplier
   }

2-4. Same as happy path
   ↓
5. CRUD layer validates:
   - Supplier exists ✅
   - Specialty matches: "Action Figures" ≠ "Dolls" ❌
   - Raises ValueError
   ↓
6. Routes layer catches ValueError
   ↓
7. Routes raises HTTPException(400)
   ↓
8. FastAPI returns error response
   {
     "detail": "Supplier specialty \"Action Figures\" does not match toy category \"Dolls\". A supplier can only provide toys in their specialty category."
   }
```

---

## 🧪 Testing Architecture

### Test Fixtures (`tests/conftest.py`)

**Purpose:** Ensure test isolation and repeatability

```python
@pytest.fixture(scope="function", autouse=True)
def cleanup_database():
    """Runs before and after each test."""
    # Clean before
    delete_all_toys()
    delete_all_suppliers()
    
    yield  # Test runs here
    
    # Clean after
    delete_all_toys()
    delete_all_suppliers()
```

**Benefits:**
- Each test starts with clean database
- Tests can run in any order
- Tests can be run multiple times
- No test pollution

### Test Categories

1. **Unit Tests** - Test individual functions
   - CRUD operations
   - Validation logic
   - Schema normalization

2. **Integration Tests** - Test API endpoints
   - HTTP request/response
   - Error handling
   - End-to-end workflows

3. **Schema Tests** - Test database structure
   - Table existence
   - Column properties
   - Constraints
   - Views

---

## 🚀 Performance Considerations

### Database Indexes

**Current:**
- Primary keys automatically indexed
- Unique constraints automatically indexed

**Potential additions for scale:**
```sql
-- Index for filtering toys by category
CREATE INDEX idx_toys_category ON toys(category);

-- Index for filtering toys by price
CREATE INDEX idx_toys_price ON toys(price);

-- Index for critical inventory queries
CREATE INDEX idx_toys_critical ON toys(in_stock, price);
```

### Query Optimization

**Critical Inventory View:**
- Uses `LEFT JOIN` (efficient for small datasets)
- Pre-filtered with `WHERE` clause
- Ordered for user convenience

**For larger datasets, consider:**
- Materialized view with periodic refresh
- Pagination for API responses
- Caching layer (Redis)

---

## 🔐 Security Considerations

### Current Implementation

**✅ Implemented:**
- Input validation (Pydantic)
- SQL injection prevention (parameterized queries)
- Email format validation
- Database constraints

**⚠️ Not Implemented (for production):**
- Authentication/Authorization
- Rate limiting
- HTTPS/TLS
- API keys
- CORS configuration
- Input sanitization for XSS

### Production Recommendations

1. **Add Authentication:**
   ```python
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   @router.post("/suppliers")
   def create_supplier(
       supplier: schemas.SupplierCreate,
       credentials: HTTPAuthorizationCredentials = Depends(security),
       db: Session = Depends(get_db)
   ):
       # Verify token
       # ...
   ```

2. **Add Rate Limiting:**
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @router.post("/suppliers")
   @limiter.limit("10/minute")
   def create_supplier(...):
       # ...
   ```

3. **Environment Variables:**
   ```python
   import os
   
   DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")
   ```

---

## 📊 Monitoring and Logging

### Recommended Additions

1. **Logging:**
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   
   @router.post("/suppliers")
   def create_supplier(...):
       logger.info(f"Creating supplier: {supplier.name}")
       try:
           result = crud.create_supplier(db, supplier)
           logger.info(f"Supplier created: id={result['id']}")
           return result
       except Exception as e:
           logger.error(f"Failed to create supplier: {e}")
           raise
   ```

2. **Metrics:**
   - Request count per endpoint
   - Response times
   - Error rates
   - Database query times

3. **Health Checks:**
   - Database connectivity
   - Disk space
   - Memory usage

---

## 🔄 Migration Strategy

### For Existing Deployments

1. **Phase 1: Add Schema**
   ```bash
   python scripts/create_suppliers_table.py
   ```
   - Adds `suppliers` table
   - Adds nullable `supplier_id` to `toys`
   - Adds trigger and view

2. **Phase 2: Create Suppliers**
   ```bash
   python scripts/seed_suppliers.py
   ```
   - Or manually create via API

3. **Phase 3: Assign Suppliers**
   ```python
   # Bulk assignment script
   for toy in toys_without_supplier:
       supplier = find_supplier_by_category(toy.category)
       update_toy(toy.id, supplier_id=supplier.id)
   ```

4. **Phase 4: Enforce Requirement (Optional)**
   ```sql
   ALTER TABLE toys 
   ALTER COLUMN supplier_id SET NOT NULL;
   ```

---

## 📚 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.109+ | REST API |
| ASGI Server | Uvicorn | 0.27+ | Application server |
| Database | PostgreSQL | 15+ | Data storage |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Validation | Pydantic | 2.0+ | Schema validation |
| Testing | Pytest | 7.0+ | Test framework |
| HTTP Client | httpx | 0.25+ | Test client |
| Email Validation | email-validator | 2.0+ | Email format checking |
| Containerization | Docker | 20+ | Database deployment |

---

## 🎓 Best Practices Applied

1. **Separation of Concerns** - Clear layer boundaries
2. **DRY Principle** - Reusable CRUD functions
3. **Explicit is Better** - Clear error messages
4. **Fail Fast** - Early validation
5. **Defense in Depth** - Multiple validation layers
6. **Test Isolation** - Independent test runs
7. **RESTful Design** - Standard HTTP semantics
8. **Type Safety** - Pydantic schemas and type hints
9. **Documentation** - Comprehensive docstrings and guides
10. **Version Control** - Git with meaningful commits

---

## 🔮 Future Enhancements

### Potential Features

1. **Bulk Operations**
   - Import suppliers from CSV
   - Bulk toy assignment

2. **Advanced Reporting**
   - Supplier performance metrics
   - Category sales analysis
   - Inventory trends

3. **Notifications**
   - Email alerts for critical inventory
   - Webhook integrations

4. **Audit Trail**
   - Track all changes
   - User activity logs

5. **Multi-tenancy**
   - Support multiple warehouses
   - Role-based access control

---

## 📖 References

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Pytest Documentation**: https://docs.pytest.org/
