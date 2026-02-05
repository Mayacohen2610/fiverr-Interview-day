"""
CRUD operations for toys. All SQL execution logic lives here.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import schemas


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
