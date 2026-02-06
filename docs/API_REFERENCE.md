# API Reference

Complete reference for all API endpoints.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Health Check

### GET /health

Check database connectivity.

**Response:**
```json
{
  "status": "up"  // or "down"
}
```

---

## Suppliers

### GET /suppliers

List all suppliers.

**Response:** `200 OK`
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

---

### GET /suppliers/{supplier_id}

Get single supplier with toy count.

**Parameters:**
- `supplier_id` (path, integer, required)

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Action Heroes Inc",
  "email": "orders@actionheroes.com",
  "specialty": "Action Figures",
  "toy_count": 5
}
```

**Errors:**
- `404 Not Found` - Supplier doesn't exist

---

### POST /suppliers

Create a new supplier.

**Request Body:**
```json
{
  "name": "MegaToys Ltd",
  "email": "orders@megatoys.com",
  "specialty": "Building"
}
```

**Response:** `200 OK`
```json
{
  "id": 7,
  "name": "MegaToys Ltd",
  "email": "orders@megatoys.com",
  "specialty": "Building"
}
```

**Errors:**
- `409 Conflict` - Supplier name already exists
- `400 Bad Request` - Invalid email format
- `422 Unprocessable Entity` - Missing required fields

---

### PATCH /suppliers/{supplier_id}

Update supplier (partial update).

**Parameters:**
- `supplier_id` (path, integer, required)

**Request Body:** (all fields optional)
```json
{
  "name": "New Name",
  "email": "newemail@example.com",
  "specialty": "New Category"
}
```

**Response:** `200 OK`
```json
{
  "id": 7,
  "name": "New Name",
  "email": "newemail@example.com",
  "specialty": "New Category"
}
```

**Errors:**
- `404 Not Found` - Supplier doesn't exist
- `409 Conflict` - New name conflicts with existing supplier
- `400 Bad Request` - Invalid email or no fields provided

---

### DELETE /suppliers/{supplier_id}

Delete a supplier.

**Parameters:**
- `supplier_id` (path, integer, required)

**Response:** `200 OK`
```json
{
  "message": "Supplier deleted successfully"
}
```

**Errors:**
- `404 Not Found` - Supplier doesn't exist
- `409 Conflict` - Supplier has toys assigned (cannot delete)

---

## Toys

### GET /toys

List all toys with supplier information.

**Response:** `200 OK`
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

### GET /toys/filter

Filter toys by price range and/or categories.

**Query Parameters:**
- `min_price` (float, optional) - Minimum price (inclusive)
- `max_price` (float, optional) - Maximum price (inclusive)
- `categories` (string[], optional) - List of categories

**Examples:**
```
GET /toys/filter?min_price=20&max_price=50
GET /toys/filter?categories=Plush&categories=Dolls
GET /toys/filter?min_price=30&max_price=100&categories=Building
```

**Response:** `200 OK`
```json
[
  {
    "id": 3,
    "toy_name": "Building Blocks",
    "category": "Building",
    "price": 45.99,
    "in_stock": true,
    "supplier_id": 3,
    "supplier": {...}
  }
]
```

**Errors:**
- `400 Bad Request` - min_price > max_price

---

### POST /toys

Create a new toy.

**Request Body:**
```json
{
  "toy_name": "Superhero Action Figure",
  "category": "Action Figures",
  "price": 29.99,
  "in_stock": true,
  "supplier_id": 1
}
```

**Fields:**
- `toy_name` (string, required)
- `category` (string, required) - Auto-normalized to Title Case
- `price` (float, required)
- `in_stock` (boolean, optional, default: true)
- `supplier_id` (integer, required)

**Response:** `200 OK`
```json
{
  "id": 15,
  "toy_name": "Superhero Action Figure",
  "category": "Action Figures",
  "price": 29.99,
  "in_stock": true,
  "supplier_id": 1
}
```

**Errors:**
- `400 Bad Request` - Supplier doesn't exist or specialty mismatch
- `422 Unprocessable Entity` - Missing required fields

---

### PATCH /toys/{toy_id}

Update a toy (partial update).

**Parameters:**
- `toy_id` (path, integer, required)

**Request Body:** (all fields optional)
```json
{
  "price": 24.99,
  "in_stock": false,
  "supplier_id": 2
}
```

**Response:** `200 OK`
```json
{
  "id": 15,
  "toy_name": "Superhero Action Figure",
  "category": "Action Figures",
  "price": 24.99,
  "in_stock": false,
  "supplier_id": 2
}
```

**Errors:**
- `404 Not Found` - Toy doesn't exist
- `400 Bad Request` - New supplier doesn't exist, specialty mismatch, or no fields provided

---

### POST /toys/category-sale

Apply discount to all toys in a category.

**Request Body:**
```json
{
  "category": "Action Figures",
  "discount_percentage": 20
}
```

**Fields:**
- `category` (string, required) - Auto-normalized to Title Case
- `discount_percentage` (integer, required) - Between 1 and 90

**Response:** `200 OK`
```json
{
  "category": "Action Figures",
  "discount_percentage": 20,
  "toys_updated": 5,
  "message": "Successfully applied 20% discount to 5 toy(s) in category 'Action Figures'"
}
```

**Notes:**
- Minimum price of 10 is enforced (toys won't go below this)
- Only affects toys in the specified category

---

## Reports

### GET /reports/critical-inventory

Get critical inventory report.

**Criteria:**
- Toys that are out of stock, OR
- Toys with price > 200

**Response:** `200 OK`
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

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input, validation failure, business rule violation |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Unique constraint violation, delete restriction |
| 422 | Unprocessable Entity | Pydantic validation error (missing/invalid fields) |

### Example Error Responses

**400 Bad Request:**
```json
{
  "detail": "Supplier specialty \"Action Figures\" does not match toy category \"Dolls\". A supplier can only provide toys in their specialty category."
}
```

**404 Not Found:**
```json
{
  "detail": "Supplier not found"
}
```

**409 Conflict:**
```json
{
  "detail": "Cannot delete supplier: 5 toy(s) are assigned to this supplier. Please reassign or remove these toys first."
}
```

**422 Unprocessable Entity:**
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

## Data Types

### Supplier Object

```typescript
{
  id: number;
  name: string;
  email: string;  // RFC 5322 compliant
  specialty: string;  // Title Case
  toy_count?: number;  // Only in GET /suppliers/{id}
}
```

### Toy Object

```typescript
{
  id: number;
  toy_name: string;
  category: string;  // Title Case
  price: number;
  in_stock: boolean;
  supplier_id: number | null;
  supplier?: Supplier;  // Only in GET /toys
}
```

### Critical Inventory Item

```typescript
{
  id: number;
  toy_name: string;
  category: string;
  price: number;
  in_stock: boolean;
  supplier_name: string | null;
  supplier_email: string | null;
  reason: string;
}
```

---

## Notes

### Category Normalization

All categories and specialties are automatically normalized to Title Case:

- Input: `"action figures"` → Output: `"Action Figures"`
- Input: `"PLUSH"` → Output: `"Plush"`
- Input: `"  board games  "` → Output: `"Board Games"`

### Supplier Specialty Rule

**The specialty of a supplier must match the category of the toy.**

This is enforced at both application and database levels:

✅ **Valid:**
```json
// Supplier specialty: "Dolls"
// Toy category: "Dolls"
```

❌ **Invalid:**
```json
// Supplier specialty: "Action Figures"
// Toy category: "Dolls"
// Error: Specialty mismatch
```

### Price Minimum

When applying category sales, toy prices will not fall below 10:

```json
// Original price: 15
// Discount: 50%
// Result: 10 (not 7.50)
```

---

## Rate Limits

Currently no rate limiting is implemented. For production, consider:

- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Authentication

Currently no authentication is required. For production, implement:

- API keys
- JWT tokens
- OAuth2

---

## CORS

For frontend integration, configure CORS in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Pagination

Currently not implemented. For large datasets, consider:

```
GET /toys?page=1&limit=50
```

---

## Versioning

Current API version: `v1` (implicit)

For future versions, consider:

```
GET /api/v1/toys
GET /api/v2/toys
```

---

## See Also

- **[QUICK_START.md](./QUICK_START.md)** - Common operations with examples
- **[SUPPLIER_MODULE.md](./SUPPLIER_MODULE.md)** - Detailed feature documentation
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical implementation details
