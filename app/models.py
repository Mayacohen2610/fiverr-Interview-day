"""
SQLAlchemy models and table definitions.
"""
from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Toy(Base):
    """ORM model for the toys table."""

    __tablename__ = "toys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    toy_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)