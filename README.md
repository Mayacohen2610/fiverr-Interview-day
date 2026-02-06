# Toy Inventory System with Supplier Management

A FastAPI-based toy inventory management system with comprehensive supplier tracking, data integrity validation, and critical inventory reporting.

## 📚 Documentation Guide

This project has several documentation files to help you get started and understand the system:

### 🚀 **Start Here**
- **[SETUP.md](./docs/SETUP.md)** - Complete setup instructions from scratch
- **[QUICK_START.md](./docs/QUICK_START.md)** - Fast-track guide for common operations

### 📖 **Feature Documentation**
- **[SUPPLIER_MODULE.md](./docs/SUPPLIER_MODULE.md)** - Detailed supplier module features and API reference
- **[API_REFERENCE.md](./docs/API_REFERENCE.md)** - Complete API endpoint documentation

### 🧪 **Testing**
- **[TESTING.md](./docs/TESTING.md)** - How to run tests and test cleanup information

### 🏗️ **For Developers**
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Technical implementation details and design decisions

---

## ⚡ Quick Setup (30 seconds)

```bash
# 1. Start database
docker-compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python scripts/create_toys_table.py
python scripts/create_suppliers_table.py

# 4. Start server
uvicorn main:app --reload
```

Visit: http://localhost:8000/health

---

## 🎯 Key Features

### ✅ Supplier Management
- Track suppliers with unique names and validated emails
- Enforce specialty matching (suppliers can only provide toys in their specialty)
- Full CRUD operations via REST API

### ✅ Critical Inventory Reporting
- Automatic identification of critical items (out of stock OR high-value >200)
- Real-time reports with supplier contact information
- Database view for efficient querying

### ✅ Data Integrity
- Foreign key constraints between toys and suppliers
- Database triggers for specialty validation
- Application-level validation with descriptive error messages

### ✅ Comprehensive Testing
- 31 automated tests covering all features
- Automatic database cleanup between tests
- Tests for CRUD, validation, and reporting

---

## 📂 Project Structure

```
fiverr-Interview-day/
├── app/                    # Application code
│   ├── crud.py            # Database operations
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic schemas
├── scripts/               # Database migrations and utilities
│   ├── create_toys_table.py
│   ├── create_suppliers_table.py
│   ├── seed_suppliers.py
│   └── clean_test_data.py
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_api.py
│   ├── test_suppliers.py
│   ├── test_supplier_validation.py
│   ├── test_critical_inventory.py
│   └── test_db_connection.py
├── docs/                  # Documentation
├── main.py               # FastAPI application entry point
├── docker-compose.yml    # PostgreSQL database setup
└── requirements.txt      # Python dependencies
```

---

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database with triggers and views
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **Pytest** - Testing framework with fixtures
- **Docker** - Containerized database

---

## 🚦 API Endpoints Overview

### Health Check
- `GET /health` - Database connectivity check

### Suppliers
- `GET /suppliers` - List all suppliers
- `GET /suppliers/{id}` - Get supplier details
- `POST /suppliers` - Create new supplier
- `PATCH /suppliers/{id}` - Update supplier
- `DELETE /suppliers/{id}` - Delete supplier

### Toys
- `GET /toys` - List all toys
- `GET /toys/filter` - Filter toys by price/category
- `POST /toys` - Create new toy (requires supplier)
- `PATCH /toys/{id}` - Update toy
- `POST /toys/category-sale` - Apply discount to category

### Reports
- `GET /reports/critical-inventory` - Critical items report

See [API_REFERENCE.md](./docs/API_REFERENCE.md) for detailed documentation.

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_suppliers.py -v

# With coverage
pytest tests/ --cov=app
```

Tests automatically clean the database before/after each run.

---

## 📝 License

This is a project for Fiverr interview demonstration.

---

## 🤝 Support

For questions or issues:
1. Check the [SETUP.md](./docs/SETUP.md) troubleshooting section
2. Review the [TESTING.md](./docs/TESTING.md) for test-related issues
3. See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for technical details
