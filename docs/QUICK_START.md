# Quick Start Guide

Fast-track guide for common operations. For detailed setup, see [SETUP.md](./SETUP.md).

## ⚡ 30-Second Setup

```bash
docker-compose up -d
pip install -r requirements.txt
python scripts/create_toys_table.py
python scripts/create_suppliers_table.py
uvicorn main:app --reload
```

Visit: http://localhost:8000/health

---

## 📋 Common Operations

### 1. Create a Supplier

```bash
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Toy Supplier Inc",
    "email": "orders@toysupplier.com",
    "specialty": "Action Figures"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Toy Supplier Inc",
  "email": "orders@toysupplier.com",
  "specialty": "Action Figures"
}
```

### 2. List All Suppliers

```bash
curl http://localhost:8000/suppliers
```

### 3. Create a Toy (with Supplier)

**Important:** Every toy must be linked to a supplier, and the supplier's specialty must match the toy's category.

```bash
curl -X POST http://localhost:8000/toys \
  -H "Content-Type: application/json" \
  -d '{
    "toy_name": "Hero Action Figure",
    "category": "Action Figures",
    "price": 29.99,
    "in_stock": true,
    "supplier_id": 1
  }'
```

### 4. List All Toys

```bash
curl http://localhost:8000/toys
```

### 5. Filter Toys by Price Range

```bash
# Toys between $20 and $50
curl "http://localhost:8000/toys/filter?min_price=20&max_price=50"
```

### 6. Filter Toys by Category

```bash
# All plush toys
curl "http://localhost:8000/toys/filter?categories=Plush"

# Multiple categories (Plush OR Dolls)
curl "http://localhost:8000/toys/filter?categories=Plush&categories=Dolls"
```

### 7. Update a Toy

```bash
# Update price
curl -X PATCH http://localhost:8000/toys/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 24.99}'

# Mark as out of stock
curl -X PATCH http://localhost:8000/toys/1 \
  -H "Content-Type: application/json" \
  -d '{"in_stock": false}'
```

### 8. Apply Category-Wide Sale

```bash
# 20% off all Action Figures
curl -X POST http://localhost:8000/toys/category-sale \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Action Figures",
    "discount_percentage": 20
  }'
```

### 9. Get Critical Inventory Report

Shows toys that are out of stock OR high-value (>200):

```bash
curl http://localhost:8000/reports/critical-inventory
```

**Response:**
```json
[
  {
    "id": 5,
    "toy_name": "Premium Dollhouse",
    "category": "Dolls",
    "price": 249.99,
    "in_stock": true,
    "supplier_name": "Dolls Supplier",
    "supplier_email": "contact@dollssupplier.com",
    "reason": "High-value item (>200)"
  },
  {
    "id": 12,
    "toy_name": "Robot Kit",
    "category": "Educational",
    "price": 45.99,
    "in_stock": false,
    "supplier_name": "Educational Toys Supplier",
    "supplier_email": "orders@edutoys.com",
    "reason": "Out of stock"
  }
]
```

### 10. Update Supplier Information

```bash
# Update email
curl -X PATCH http://localhost:8000/suppliers/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "newemail@supplier.com"}'
```

### 11. Delete a Supplier

**Note:** Cannot delete a supplier if they have toys assigned.

```bash
curl -X DELETE http://localhost:8000/suppliers/1
```

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_suppliers.py -v
pytest tests/test_supplier_validation.py -v
pytest tests/test_critical_inventory.py -v

# With output
pytest tests/ -v -s
```

**Note:** Tests automatically clean the database before and after each test run.

---

## 🔍 Exploring the API

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces let you:
- See all available endpoints
- Try out API calls directly in the browser
- View request/response schemas
- See validation requirements

---

## 🎯 Common Workflows

### Workflow 1: Adding a New Product Line

```bash
# 1. Create the supplier
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LEGO Distributor",
    "email": "orders@legodist.com",
    "specialty": "Building"
  }'

# 2. Add toys from this supplier
curl -X POST http://localhost:8000/toys \
  -H "Content-Type: application/json" \
  -d '{
    "toy_name": "LEGO City Set",
    "category": "Building",
    "price": 79.99,
    "in_stock": true,
    "supplier_id": 7
  }'
```

### Workflow 2: Restocking Critical Items

```bash
# 1. Get critical inventory report
curl http://localhost:8000/reports/critical-inventory > critical.json

# 2. Review items that need restocking
# (Items with "reason": "Out of stock")

# 3. Update stock status after restocking
curl -X PATCH http://localhost:8000/toys/12 \
  -H "Content-Type: application/json" \
  -d '{"in_stock": true}'
```

### Workflow 3: Seasonal Sale

```bash
# Apply 30% discount to all Board Games for holiday season
curl -X POST http://localhost:8000/toys/category-sale \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Board Games",
    "discount_percentage": 30
  }'
```

---

## 🛑 Common Errors and Solutions

### Error: 409 Conflict - Supplier name already exists

**Cause:** Supplier names must be unique.

**Solution:** Use a different name or update the existing supplier.

### Error: 400 Bad Request - Supplier specialty does not match toy category

**Cause:** The "Specialty Rule" - suppliers can only provide toys in their specialty.

**Solution:** Either:
- Change the toy's category to match the supplier's specialty, OR
- Use a different supplier whose specialty matches the toy's category

### Error: 400 Bad Request - Supplier does not exist

**Cause:** The `supplier_id` doesn't exist in the database.

**Solution:** Create the supplier first, or use a valid `supplier_id`.

### Error: 422 Unprocessable Entity - Invalid email

**Cause:** Email format is invalid.

**Solution:** Use a valid email format (e.g., `user@domain.com`).

### Error: 409 Conflict - Cannot delete supplier

**Cause:** Supplier has toys assigned (foreign key constraint).

**Solution:** Either:
- Reassign the toys to a different supplier, OR
- Delete the toys first, then delete the supplier

---

## 🗄️ Database Access

### Web UI (Adminer)

http://localhost:8080

Login:
- Server: `postgres`
- Username: `admin`
- Password: `admin123`
- Database: `fiverr_db`

### Command Line (psql)

```bash
docker exec -it fiverr_postgres psql -U admin -d fiverr_db
```

---

## 🧹 Cleanup and Reset

### Clean Test Data

```bash
python scripts/clean_test_data.py
```

### Complete Database Reset

```bash
docker-compose down -v
docker-compose up -d
python scripts/create_toys_table.py
python scripts/create_suppliers_table.py
python scripts/seed_suppliers.py
```

---

## 📚 Next Steps

- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API documentation
- **[SUPPLIER_MODULE.md](./SUPPLIER_MODULE.md)** - Detailed feature documentation
- **[TESTING.md](./TESTING.md)** - Testing guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical details

---

## 💡 Tips

1. **Category Normalization:** Categories are automatically normalized to Title Case:
   - `"action figures"` → `"Action Figures"`
   - `"PLUSH"` → `"Plush"`

2. **Price Minimum:** The category sale endpoint ensures no toy price falls below 10.

3. **Critical Threshold:** Items are considered critical if price > 200 OR out of stock.

4. **Supplier Specialty:** Must exactly match toy categories (case-insensitive due to normalization).

5. **Test Isolation:** Tests automatically clean the database, so you can run them repeatedly without conflicts.
