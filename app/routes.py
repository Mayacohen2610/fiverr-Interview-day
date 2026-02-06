"""
API route definitions.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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


# ============================================================================
# Supplier Endpoints
# ============================================================================


@router.get("/suppliers")
def get_all_suppliers(db: Session = Depends(get_db)):
    """
    Returns all suppliers in the database.
    Each supplier includes id, name, email, and specialty.
    """
    return crud.get_all_suppliers(db)


@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    Returns a single supplier by id with toy count.
    Returns 404 if supplier doesn't exist.
    """
    result = crud.get_supplier_by_id(db, supplier_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return result


@router.post("/suppliers")
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    """
    Creates a new supplier.
    Email is validated by Pydantic (RFC 5322 compliant).
    Supplier name must be unique.
    Returns the created supplier with its assigned id.
    """
    try:
        return crud.create_supplier(db, supplier)
    except IntegrityError as e:
        # Handle unique constraint violation or CHECK constraint violation
        if "unique constraint" in str(e).lower() or "suppliers_name_key" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A supplier with the name '{supplier.name}' already exists"
            )
        elif "check constraint" in str(e).lower() or "email" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid email format: {supplier.email}"
            )
        raise HTTPException(status_code=400, detail="Failed to create supplier")


@router.patch("/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: int, 
    update: schemas.SupplierUpdate, 
    db: Session = Depends(get_db)
):
    """
    Partially updates a supplier by id. Only provided fields are updated.
    Returns the updated supplier, or 404 if no supplier exists with the given id.
    Email is re-validated by Pydantic if changed.
    """
    updates = update.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    try:
        result = crud.update_supplier(db, supplier_id, update)
        if result is None:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return result
    except IntegrityError as e:
        if "unique constraint" in str(e).lower() or "suppliers_name_key" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"A supplier with the name '{update.name}' already exists"
            )
        elif "check constraint" in str(e).lower() or "email" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid email format: {update.email}"
            )
        raise HTTPException(status_code=400, detail="Failed to update supplier")


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    Deletes a supplier by id.
    Cannot delete supplier if they have toys assigned (foreign key constraint).
    Returns 404 if supplier doesn't exist.
    Returns 409 if supplier has toys and cannot be deleted.
    """
    # First check if supplier exists
    supplier = crud.get_supplier_by_id(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Check if supplier has toys
    if supplier.get("toy_count", 0) > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete supplier: {supplier['toy_count']} toy(s) are assigned to this supplier. "
                   "Please reassign or remove these toys first."
        )
    
    # Attempt deletion
    success = crud.delete_supplier(db, supplier_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete supplier")
    
    return {"message": "Supplier deleted successfully"}


# ============================================================================
# Toy Endpoints
# ============================================================================


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
    Adds a new toy to the toys table with supplier validation.
    Requires supplier_id - the toy must be linked to an existing supplier.
    Validates that the supplier's specialty matches the toy's category.
    Returns the created toy with its assigned id.
    """
    try:
        return crud.create_toy(db, toy)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        # Handle database trigger errors
        if "validate_supplier_specialty" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail="Supplier specialty does not match toy category"
            )
        raise HTTPException(status_code=400, detail="Failed to create toy")


@router.patch("/toys/{toy_id}")
def update_toy(toy_id: int, update: schemas.ToyUpdate, db: Session = Depends(get_db)):
    """
    Partially updates a toy by its id. Only provided fields are updated.
    Supports price, in_stock, and/or supplier_id; omitting a field leaves it unchanged.
    If supplier_id is updated, validates that the supplier exists and specialty matches.
    Returns the updated toy, or 404 if no toy exists with the given id.
    """
    updates = update.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = crud.update_toy(db, toy_id, update)
        if result is None:
            raise HTTPException(status_code=404, detail="Toy not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        # Handle database trigger errors
        if "validate_supplier_specialty" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="Supplier specialty does not match toy category"
            )
        raise HTTPException(status_code=400, detail="Failed to update toy")


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


# ============================================================================
# Report Endpoints
# ============================================================================


@router.get("/reports/critical-inventory")
def get_critical_inventory_report(db: Session = Depends(get_db)):
    """
    Returns the critical inventory report.
    
    Critical items include:
    - Toys that are out of stock, OR
    - High-value toys (price > 200)
    
    Each item includes toy details and supplier contact information
    for easy restocking.
    """
    return crud.get_critical_inventory(db)
