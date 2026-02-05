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
    Returns all toys from the toys table.
    Each toy includes id, toy_name, category, price, and in_stock.
    """
    result = db.execute(
        text("SELECT id, toy_name, category, price, in_stock FROM toys ORDER BY id")
    )
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


def create_toy(db: Session, toy: schemas.ToyCreate) -> dict:
    """
    Inserts a new toy into the toys table.
    Returns the created toy with its assigned id.
    """
    result = db.execute(
        text("""
            INSERT INTO toys (toy_name, category, price, in_stock)
            VALUES (:toy_name, :category, :price, :in_stock)
            RETURNING id, toy_name, category, price, in_stock
        """),
        {
            "toy_name": toy.toy_name,
            "category": toy.category,
            "price": toy.price,
            "in_stock": toy.in_stock,
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
    }


def update_toy(db: Session, toy_id: int, update: schemas.ToyUpdate) -> dict | None:
    """
    Partially updates a toy by id. Only provided fields are updated.
    Returns the updated toy dict, or None if no toy exists with the given id.
    Caller must ensure at least one field is provided.
    """
    updates = update.model_dump(exclude_unset=True)
    set_parts = [f"{k} = :{k}" for k in updates.keys()]
    set_clause = ", ".join(set_parts)
    params = dict(updates, toy_id=toy_id)

    result = db.execute(
        text(f"""
            UPDATE toys
            SET {set_clause}
            WHERE id = :toy_id
            RETURNING id, toy_name, category, price, in_stock
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
