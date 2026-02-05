"""
Pydantic schemas for request/response validation.
"""
from typing import Optional

from pydantic import BaseModel


class ToyCreate(BaseModel):
    """Request body for creating a new toy."""

    toy_name: str
    category: str
    price: float
    in_stock: bool = True


class ToyUpdate(BaseModel):
    """Request body for partial update of a toy. All fields are optional."""

    price: Optional[float] = None
    in_stock: Optional[bool] = None


class ToyResponse(BaseModel):
    """Response schema for a toy."""

    id: int
    toy_name: str
    category: str
    price: float
    in_stock: bool
