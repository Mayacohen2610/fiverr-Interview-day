"""
Pydantic schemas for request/response validation.
"""
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, BeforeValidator


def normalize_category_value(value: str) -> str:
    """
    Normalizes the category by stripping whitespace and converting to title case.
    Examples: "action figures" -> "Action Figures", "  PLUSH  " -> "Plush"
    """
    return value.strip().title()


# Custom type that automatically normalizes category values
NormalizedCategory = Annotated[str, BeforeValidator(normalize_category_value)]


class SupplierCreate(BaseModel):
    """Request body for creating a new supplier."""

    name: str
    email: EmailStr
    specialty: NormalizedCategory


class SupplierUpdate(BaseModel):
    """Request body for partial update of a supplier. All fields are optional."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    specialty: Optional[NormalizedCategory] = None


class SupplierResponse(BaseModel):
    """Response schema for a supplier."""

    id: int
    name: str
    email: str
    specialty: str


class ToyCreate(BaseModel):
    """Request body for creating a new toy."""

    toy_name: str
    category: NormalizedCategory
    price: float
    in_stock: bool = True
    supplier_id: int


class ToyUpdate(BaseModel):
    """Request body for partial update of a toy. All fields are optional."""

    price: Optional[float] = None
    in_stock: Optional[bool] = None
    supplier_id: Optional[int] = None


class ToyResponse(BaseModel):
    """Response schema for a toy."""

    id: int
    toy_name: str
    category: str
    price: float
    in_stock: bool
    supplier_id: Optional[int] = None
    supplier: Optional[SupplierResponse] = None


class CategorySale(BaseModel):
    """Request body for applying a discount to all toys in a category."""

    category: NormalizedCategory
    discount_percentage: int = Field(ge=1, le=90, description="Discount percentage (1-90)")


class CriticalInventoryItem(BaseModel):
    """Response schema for critical inventory report items."""

    id: int
    toy_name: str
    category: str
    price: float
    in_stock: bool
    supplier_name: Optional[str] = None
    supplier_email: Optional[str] = None
    reason: str
