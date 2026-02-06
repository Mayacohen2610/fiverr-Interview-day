# Supplier & Reliability Module

Comprehensive supplier management and critical inventory reporting for the toy inventory system.

## 📋 Features Overview

### 1. Supplier Management

Every supplier has:
- **Unique name** - No duplicate supplier names allowed
- **Contact email** - RFC 5322 validated email address
- **Specialty** - Must match toy categories (e.g., "Action Figures", "Dolls")

### 2. Data Integrity Rules

#### The Specialty Rule ⭐
A supplier can only provide toys that match their specialty category.

**Example:**
- ✅ A "Dolls" supplier CAN supply a "Dolls" toy
- ❌ A "Dolls" supplier CANNOT supply an "Action Figures" toy

This is enforced at **two levels**:
1. **Application layer** - Fast feedback with user-friendly error messages
2. **Database trigger** - Safety net against direct SQL access

#### Foreign Key Constraint
- Toys must be linked to an existing supplier
- Cannot delete a supplier that has toys assigned
- Existing toys can have `supplier_id = NULL` (for migration purposes)

### 3. Critical Inventory Report

The warehouse manager can view toys that need attention:

**Critical items include:**
- Toys that are **out of stock** (need restocking)
- High-value toys with **price > 200** (require monitoring)

Each report entry includes supplier contact information for easy restocking.

---

## 🔌 API Endpoints

### Supplier Endpoints

#### List All Suppliers
```http
GET /suppliers
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Action Heroes Inc",
    "email": "orders@actionheroes.com",
    "specialty": "Action Figures"
  }
]
```

#### Get Single Supplier
```http
GET /suppliers/{supplier_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Action Heroes Inc",
  "email": "orders@actionheroes.com",
  "specialty": "Action Figures",
  "toy_count": 5
}
```

#### Create Supplier
```http
POST /suppliers
Content-Type: application/json

{
  "name": "MegaToys Ltd",
  "email": "orders@megatoys.com",
  "specialty": "Building"
}
```

**Validations:**
- Email must be valid format
- Name must be unique
- Specialty is normalized to Title Case

**Error Responses:**
- `409 Conflict` - Supplier name already exists
- `400 Bad Request` - Invalid email format
- `422 Unprocessable Entity` - Missing required fields

#### Update Supplier
```http
PATCH /suppliers/{supplier_id}
Content-Type: application/json

{
  "email": "newemail@megatoys.com"
}
```

Only provided fields are updated. Partial updates supported.

**Error Responses:**
- `404 Not Found` - Supplier doesn't exist
- `409 Conflict` - New name conflicts with existing supplier
- `400 Bad Request` - Invalid email format or no fields to update

#### Delete Supplier
```http
DELETE /suppliers/{supplier_id}
```

**Error Responses:**
- `404 Not Found` - Supplier doesn't exist
- `409 Conflict` - Cannot delete supplier with toys assigned

**Success Response:**
```json
{
  "message": "Supplier deleted successfully"
}
```

---

### Modified Toy Endpoints

#### Create Toy (Now Requires Supplier)
```http
POST /toys
Content-Type: application/json

{
  "toy_name": "Superhero Action Figure",
  "category": "Action Figures",
  "price": 29.99,
  "in_stock": true,
  "supplier_id": 1
}
```

**Validations:**
- `supplier_id` is required
- Supplier must exist
- Supplier specialty must match toy category

**Error Responses:**
- `400 Bad Request` - Supplier doesn't exist or specialty mismatch
- `422 Unprocessable Entity` - Missing supplier_id

#### Update Toy (Can Change Supplier)
```http
PATCH /toys/{toy_id}
Content-Type: application/json

{
  "supplier_id": 2,
  "price": 24.99
}
```

When updating `supplier_id`, the new supplier's specialty is validated.

**Error Responses:**
- `404 Not Found` - Toy doesn't exist
- `400 Bad Request` - New supplier doesn't exist or specialty mismatch

#### List Toys (Now Includes Supplier Info)
```http
GET /toys
```

**Response:**
```json
[
  {
    "id": 1,
    "toy_name": "Superhero Figure",
    "category": "Action Figures",
    "price": 29.99,
    "in_stock": true,
    "supplier_id": 1,
    "supplier": {
      "id": 1,
      "name": "Action Heroes Inc",
      "email": "orders@actionheroes.com",
      "specialty": "Action Figures"
    }
  }
]
```

---

### Report Endpoints

#### Critical Inventory Report
```http
GET /reports/critical-inventory
```

Returns toys that are out of stock OR high-value (price > 200).

**Response:**
```json
[
  {
    "id": 5,
    "toy_name": "Premium Doll House",
    "category": "Dolls",
    "price": 250.00,
    "in_stock": true,
    "supplier_name": "DollWorld Inc",
    "supplier_email": "restock@dollworld.com",
    "reason": "High-value item (>200)"
  },
  {
    "id": 12,
    "toy_name": "Sold Out Teddy",
    "category": "Plush",
    "price": 15.00,
    "in_stock": false,
    "supplier_name": "Plush Paradise",
    "supplier_email": "contact@plushparadise.com",
    "reason": "Out of stock"
  },
  {
    "id": 8,
    "toy_name": "Luxury Train Set",
    "category": "Building",
    "price": 299.99,
    "in_stock": false,
    "supplier_name": "Building Blocks Co",
    "supplier_email": "orders@buildingblocks.com",
    "reason": "Out of stock, High-value item (>200)"
  }
]
```

**Reason Values:**
- `"Out of stock"` - Item needs restocking
- `"High-value item (>200)"` - Expensive item requiring monitoring
- `"Out of stock, High-value item (>200)"` - Both conditions met

---

## 💡 Usage Examples

### Complete Workflow: Adding a New Product Line

```bash
# 1. Create a supplier
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DollWorld Inc",
    "email": "orders@dollworld.com",
    "specialty": "Dolls"
  }'

# Response: {"id": 1, "name": "DollWorld Inc", ...}

# 2. Create toys with this supplier
curl -X POST http://localhost:8000/toys \
  -H "Content-Type: application/json" \
  -d '{
    "toy_name": "Classic Porcelain Doll",
    "category": "Dolls",
    "price": 45.99,
    "in_stock": true,
    "supplier_id": 1
  }'

# 3. Create another toy
curl -X POST http://localhost:8000/toys \
  -H "Content-Type: application/json" \
  -d '{
    "toy_name": "Premium Dollhouse",
    "category": "Dolls",
    "price": 249.99,
    "in_stock": true,
    "supplier_id": 1
  }'

# 4. Check supplier details (includes toy count)
curl http://localhost:8000/suppliers/1
# Response: {..., "toy_count": 2}
```

### Workflow: Handling Out of Stock Items

```bash
# 1. Mark toy as out of stock
curl -X PATCH http://localhost:8000/toys/1 \
  -H "Content-Type: application/json" \
  -d '{"in_stock": false}'

# 2. Check critical inventory report
curl http://localhost:8000/reports/critical-inventory

# 3. Contact supplier using email from report
# (Use supplier_email to request restock)

# 4. After restocking, update inventory
curl -X PATCH http://localhost:8000/toys/1 \
  -H "Content-Type: application/json" \
  -d '{"in_stock": true}'
```

### Workflow: Changing Suppliers

```bash
# Scenario: Need to switch to a different supplier for a toy

# 1. Create new supplier (if needed)
curl -X POST http://localhost:8000/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alternative Dolls Supplier",
    "email": "contact@altdolls.com",
    "specialty": "Dolls"
  }'
# Response: {"id": 2, ...}

# 2. Update toy to use new supplier
curl -X PATCH http://localhost:8000/toys/1 \
  -H "Content-Type: application/json" \
  -d '{"supplier_id": 2}'

# Note: Specialty must still match!
```

---

## 🎯 Business Rules Summary

1. **Every toy must have a supplier** (after migration period)
2. **Supplier specialty must match toy category** (enforced at app + DB level)
3. **Cannot delete suppliers with active toys**
4. **Supplier names must be unique**
5. **All emails are validated** (RFC 5322 compliant)
6. **Critical items = out of stock OR price > 200**
7. **Categories are normalized** to Title Case automatically

---

## 🔧 Error Handling Reference

### 400 Bad Request
- Invalid email format
- Supplier doesn't exist
- Specialty mismatch between supplier and toy
- No fields provided for update

**Example:**
```json
{
  "detail": "Supplier specialty \"Action Figures\" does not match toy category \"Dolls\". A supplier can only provide toys in their specialty category."
}
```

### 404 Not Found
- Supplier not found
- Toy not found

**Example:**
```json
{
  "detail": "Supplier not found"
}
```

### 409 Conflict
- Duplicate supplier name
- Cannot delete supplier with toys

**Example:**
```json
{
  "detail": "Cannot delete supplier: 5 toy(s) are assigned to this supplier. Please reassign or remove these toys first."
}
```

### 422 Unprocessable Entity
- Pydantic validation errors (automatic)
- Missing required fields
- Invalid data types

**Example:**
```json
{
  "detail": [
    {
      "loc": ["body", "supplier_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🔄 Migration Notes

For existing deployments:
- `supplier_id` is nullable to allow gradual migration
- Existing toys can operate without suppliers temporarily
- Use PATCH endpoint to assign suppliers to existing toys
- Consider creating a bulk assignment endpoint for large datasets

**Migration Strategy:**
1. Run `scripts/create_suppliers_table.py` to add schema
2. Create suppliers for all existing categories
3. Gradually assign suppliers to existing toys
4. Once complete, consider making `supplier_id` NOT NULL

---

## 📚 See Also

- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API documentation
- **[QUICK_START.md](./QUICK_START.md)** - Common operations guide
- **[TESTING.md](./TESTING.md)** - Testing guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical implementation details
