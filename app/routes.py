"""
API route definitions.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.get("/toys/filter")
def get_toys_by_filters(
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price (inclusive)"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price (inclusive)"),
    categories: Optional[list[str]] = Query(None, description="List of categories to filter by"),
    db: Session = Depends(get_db),
):
    """
    Returns toys filtered by price range and/or categories.
    All query parameters are optional.
    
    Examples:
    - /toys/filter?min_price=30&max_price=100 - toys between $30 and $100
    - /toys/filter?categories=Plush&categories=Action Figures - toys in Plush OR Action Figures
    - /toys/filter?min_price=20&max_price=50&categories=Building - Building toys between $20-$50
    - /toys/filter?categories=plush toys&categories=BOARD GAMES - categories are normalized to Title Case
    - /toys/filter - all toys (no filter)
    
    Results are ordered by price (ascending).
    """
    # Validate that min_price is not greater than max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price"
        )
    
    return crud.get_toys_by_price_range(db, min_price, max_price, categories)


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


@router.post("/toys/category-sale")
def apply_category_sale(sale: schemas.CategorySale, db: Session = Depends(get_db)):
    """
    Applies a discount to all toys in the specified category.
    Discount percentage must be between 1 and 90.
    Ensures that no toy's price falls below the minimum price of 10.
    Returns summary of updated toys count and operation details.
    """
    result = crud.apply_category_sale(
        db, sale.category, sale.discount_percentage
    )
    return result
