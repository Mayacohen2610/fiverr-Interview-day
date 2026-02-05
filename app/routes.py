"""
API route definitions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/health")
def health():
    """
    Health check endpoint that verifies PostgreSQL connectivity.
    Returns {"status": "up"} when the database is reachable, {"status": "down"} otherwise.
    """
    if crud.check_db_connection():
        return {"status": "up"}
    return {"status": "down"}


@router.get("/toys")
def get_all_toys(db: Session = Depends(get_db)):
    """
    Returns all toys in the toys table.
    Each toy includes id, toy_name, category, price, and in_stock.
    """
    return crud.get_all_toys(db)


@router.post("/toys")
def add_toy(toy: schemas.ToyCreate, db: Session = Depends(get_db)):
    """
    Adds a new toy to the toys table.
    Accepts toy_name, category, price, and optional in_stock (defaults to True).
    Returns the created toy with its assigned id.
    """
    return crud.create_toy(db, toy)


@router.patch("/toys/{toy_id}")
def update_toy(toy_id: int, update: schemas.ToyUpdate, db: Session = Depends(get_db)):
    """
    Partially updates a toy by its id. Only provided fields are updated.
    Supports price and/or in_stock; omitting a field leaves it unchanged.
    Returns the updated toy, or 404 if no toy exists with the given id.
    """
    updates = update.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = crud.update_toy(db, toy_id, update)
    if result is None:
        raise HTTPException(status_code=404, detail="Toy not found")
    return result
