"""
CRUD operations for toys. All SQL execution logic lives here.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import schemas

# Minimum price constraint for category sales
MIN_PRICE = 10.0


def check_db_connection() -> bool:
    """
    Verifies PostgreSQL connectivity.
    Returns True if database is reachable, False otherwise.
    """
    from app.database import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_all_toys(db: Session) -> list[dict]:
    """
    Returns all toys from the toys table with supplier information.
    Each toy includes id, toy_name, category, price, in_stock, supplier_id, and supplier details.
    """
    result = db.execute(
        text("""
            SELECT t.id, t.toy_name, t.category, t.price, t.in_stock, t.supplier_id,
                   s.id as s_id, s.name, s.email, s.specialty
            FROM toys t
            LEFT JOIN suppliers s ON t.supplier_id = s.id
            ORDER BY t.id
        """)
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "toy_name": row[1],
            "category": row[2],
            "price": row[3],
            "in_stock": row[4],
            "supplier_id": row[5],
            "supplier": {
                "id": row[6],
                "name": row[7],
                "email": row[8],
                "specialty": row[9],
            } if row[6] is not None else None,
        }
        for row in rows
    ]


def create_toy(db: Session, toy: schemas.ToyCreate) -> dict:
    """
    Inserts a new toy into the toys table with supplier validation.
    Validates that:
    1. The supplier exists
    2. The supplier's specialty matches the toy's category
    Returns the created toy with its assigned id.
    Raises ValueError if validation fails.
    """
    # Validate supplier exists and specialty matches category
    result = db.execute(
        text("SELECT specialty FROM suppliers WHERE id = :supplier_id"),
        {"supplier_id": toy.supplier_id},
    )
    row = result.fetchone()
    if row is None:
        raise ValueError(f"Supplier with id {toy.supplier_id} does not exist")
    
    supplier_specialty = row[0]
    if supplier_specialty != toy.category:
        raise ValueError(
            f'Supplier specialty "{supplier_specialty}" does not match toy category "{toy.category}". '
            f"A supplier can only provide toys in their specialty category."
        )
    
    # Insert toy with supplier_id
    result = db.execute(
        text("""
            INSERT INTO toys (toy_name, category, price, in_stock, supplier_id)
            VALUES (:toy_name, :category, :price, :in_stock, :supplier_id)
            RETURNING id, toy_name, category, price, in_stock, supplier_id
        """),
        {
            "toy_name": toy.toy_name,
            "category": toy.category,
            "price": toy.price,
            "in_stock": toy.in_stock,
            "supplier_id": toy.supplier_id,
        },
    )
    db.commit()
    row = result.fetchone()
    return {
        "id": row[0],
        "toy_name": row[1],
        "category": row[2],
        "price": row[3],
        "in_stock": row[4],
        "supplier_id": row[5],
    }


def update_toy(db: Session, toy_id: int, update: schemas.ToyUpdate) -> dict | None:
    """
    Partially updates a toy by id. Only provided fields are updated.
    If supplier_id is being updated, validates that:
    1. The new supplier exists
    2. The supplier's specialty matches the toy's category
    Returns the updated toy dict, or None if no toy exists with the given id.
    Raises ValueError if supplier validation fails.
    Caller must ensure at least one field is provided.
    """
    updates = update.model_dump(exclude_unset=True)
    
    # If supplier_id is being updated, validate it
    if "supplier_id" in updates:
        # Get toy's category
        result = db.execute(
            text("SELECT category FROM toys WHERE id = :toy_id"),
            {"toy_id": toy_id},
        )
        toy_row = result.fetchone()
        if toy_row is None:
            return None  # Toy doesn't exist
        
        toy_category = toy_row[0]
        
        # Validate supplier exists and specialty matches
        result = db.execute(
            text("SELECT specialty FROM suppliers WHERE id = :supplier_id"),
            {"supplier_id": updates["supplier_id"]},
        )
        supplier_row = result.fetchone()
        if supplier_row is None:
            raise ValueError(f"Supplier with id {updates['supplier_id']} does not exist")
        
        supplier_specialty = supplier_row[0]
        if supplier_specialty != toy_category:
            raise ValueError(
                f'Supplier specialty "{supplier_specialty}" does not match toy category "{toy_category}". '
                f"A supplier can only provide toys in their specialty category."
            )
    
    set_parts = [f"{k} = :{k}" for k in updates.keys()]
    set_clause = ", ".join(set_parts)
    params = dict(updates, toy_id=toy_id)

    result = db.execute(
        text(f"""
            UPDATE toys
            SET {set_clause}
            WHERE id = :toy_id
            RETURNING id, toy_name, category, price, in_stock, supplier_id
        """),
        params,
    )
    db.commit()
    row = result.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "toy_name": row[1],
        "category": row[2],
        "price": row[3],
        "in_stock": row[4],
        "supplier_id": row[5],
    }


def apply_category_sale(
    db: Session, category: str, discount_percentage: int
) -> dict:
    """
    Applies a discount to all toys in the specified category.
    Ensures discounted prices don't fall below MIN_PRICE (10.0).
    Returns a summary of the operation with count of updated toys and applied prices.
    """
    # Calculate discount multiplier (e.g., 20% discount = 0.80)
    discount_multiplier = (100 - discount_percentage) / 100

    # Fetch all toys in the category to calculate new prices
    result = db.execute(
        text("SELECT id, price FROM toys WHERE category = :category"),
        {"category": category},
    )
    toys = result.fetchall()

    if not toys:
        return {"updated_count": 0, "category": category, "message": "No toys found in this category"}

    # Update each toy's price with discount, ensuring MIN_PRICE constraint
    updated_count = 0
    for toy_id, current_price in toys:
        new_price = current_price * discount_multiplier
        # Ensure price doesn't go below MIN_PRICE
        final_price = max(new_price, MIN_PRICE)

        db.execute(
            text("UPDATE toys SET price = :price WHERE id = :toy_id"),
            {"price": final_price, "toy_id": toy_id},
        )
        updated_count += 1

    db.commit()

    return {
        "updated_count": updated_count,
        "category": category,
        "discount_percentage": discount_percentage,
        "min_price_enforced": MIN_PRICE,
        "message": f"Successfully applied {discount_percentage}% discount to {updated_count} toy(s) in category '{category}'",
    }


def get_toys_by_price_range(
    db: Session,
    min_price: float | None = None,
    max_price: float | None = None,
    categories: list[str] | None = None,
) -> list[dict]:
    """
    Returns all toys within the specified price range and/or categories.
    All parameters are optional:
    - min_price: Minimum price (inclusive)
    - max_price: Maximum price (inclusive)
    - categories: List of categories to filter by (normalized to title case)
    
    If no parameters are provided, returns all toys.
    If categories are provided, returns toys in ANY of those categories (OR logic).
    """
    # Build dynamic WHERE clause based on provided parameters
    conditions = []
    params = {}

    if min_price is not None:
        conditions.append("price >= :min_price")
        params["min_price"] = min_price

    if max_price is not None:
        conditions.append("price <= :max_price")
        params["max_price"] = max_price

    # Handle multiple categories with IN clause
    if categories is not None and len(categories) > 0:
        # Normalize categories to match stored format
        from app.schemas import normalize_category_value
        normalized_categories = [normalize_category_value(cat) for cat in categories]
        
        # Create placeholders for IN clause
        placeholders = ", ".join([f":cat_{i}" for i in range(len(normalized_categories))])
        conditions.append(f"category IN ({placeholders})")
        
        # Add category parameters
        for i, cat in enumerate(normalized_categories):
            params[f"cat_{i}"] = cat

    # Construct the query
    base_query = "SELECT id, toy_name, category, price, in_stock FROM toys"
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
        query = base_query + where_clause + " ORDER BY price ASC, id"
    else:
        query = base_query + " ORDER BY price ASC, id"

    result = db.execute(text(query), params)
    rows = result.fetchall()

    return [
        {
            "id": row[0],
            "toy_name": row[1],
            "category": row[2],
            "price": row[3],
            "in_stock": row[4],
        }
        for row in rows
    ]


# ============================================================================
# Supplier CRUD Operations
# ============================================================================


def get_all_suppliers(db: Session) -> list[dict]:
    """
    Returns all suppliers from the suppliers table.
    Each supplier includes id, name, email, and specialty.
    """
    result = db.execute(
        text("SELECT id, name, email, specialty FROM suppliers ORDER BY id")
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "specialty": row[3],
        }
        for row in rows
    ]


def get_supplier_by_id(db: Session, supplier_id: int) -> dict | None:
    """
    Returns a single supplier by id with toy count.
    Returns None if supplier doesn't exist.
    """
    result = db.execute(
        text("""
            SELECT s.id, s.name, s.email, s.specialty, COUNT(t.id) as toy_count
            FROM suppliers s
            LEFT JOIN toys t ON s.id = t.supplier_id
            WHERE s.id = :supplier_id
            GROUP BY s.id, s.name, s.email, s.specialty
        """),
        {"supplier_id": supplier_id},
    )
    row = result.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "specialty": row[3],
        "toy_count": row[4],
    }


def create_supplier(db: Session, supplier: schemas.SupplierCreate) -> dict:
    """
    Inserts a new supplier into the suppliers table.
    Email validation is handled by Pydantic EmailStr.
    Returns the created supplier with its assigned id.
    Raises exception if supplier name already exists (unique constraint).
    """
    result = db.execute(
        text("""
            INSERT INTO suppliers (name, email, specialty)
            VALUES (:name, :email, :specialty)
            RETURNING id, name, email, specialty
        """),
        {
            "name": supplier.name,
            "email": supplier.email,
            "specialty": supplier.specialty,
        },
    )
    db.commit()
    row = result.fetchone()
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "specialty": row[3],
    }


def update_supplier(
    db: Session, supplier_id: int, update: schemas.SupplierUpdate
) -> dict | None:
    """
    Partially updates a supplier by id. Only provided fields are updated.
    Returns the updated supplier dict, or None if no supplier exists with the given id.
    Email re-validation is handled by Pydantic if email is changed.
    """
    updates = update.model_dump(exclude_unset=True)
    if not updates:
        return None  # No updates provided
    
    set_parts = [f"{k} = :{k}" for k in updates.keys()]
    set_clause = ", ".join(set_parts)
    params = dict(updates, supplier_id=supplier_id)

    result = db.execute(
        text(f"""
            UPDATE suppliers
            SET {set_clause}
            WHERE id = :supplier_id
            RETURNING id, name, email, specialty
        """),
        params,
    )
    db.commit()
    row = result.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "specialty": row[3],
    }


def delete_supplier(db: Session, supplier_id: int) -> bool:
    """
    Deletes a supplier by id.
    Returns False if supplier has toys (foreign key constraint prevents deletion).
    Returns False if supplier doesn't exist.
    Returns True if deletion successful.
    """
    # Check if supplier has toys
    result = db.execute(
        text("SELECT COUNT(*) FROM toys WHERE supplier_id = :supplier_id"),
        {"supplier_id": supplier_id},
    )
    toy_count = result.fetchone()[0]
    if toy_count > 0:
        return False  # Cannot delete supplier with toys
    
    # Delete supplier
    result = db.execute(
        text("DELETE FROM suppliers WHERE id = :supplier_id RETURNING id"),
        {"supplier_id": supplier_id},
    )
    db.commit()
    deleted_row = result.fetchone()
    return deleted_row is not None


# ============================================================================
# Report Functions
# ============================================================================


def get_critical_inventory(db: Session) -> list[dict]:
    """
    Returns critical inventory items from the critical_inventory_view.
    Critical items are:
    - Toys that are out of stock, OR
    - Toys with price > 200 (high value items)
    
    Returns toy details with supplier contact information.
    """
    result = db.execute(
        text("""
            SELECT id, toy_name, category, price, in_stock,
                   supplier_name, supplier_email, reason
            FROM critical_inventory_view
        """)
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "toy_name": row[1],
            "category": row[2],
            "price": row[3],
            "in_stock": row[4],
            "supplier_name": row[5],
            "supplier_email": row[6],
            "reason": row[7],
        }
        for row in rows
    ]
