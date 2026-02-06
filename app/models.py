"""
SQLAlchemy models and table definitions.
"""
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Supplier(Base):
    """ORM model for the suppliers table."""

    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=False)

    # Relationship to toys
    toys = relationship("Toy", back_populates="supplier")


class Toy(Base):
    """ORM model for the toys table."""

    __tablename__ = "toys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    toy_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    # Relationship to supplier
    supplier = relationship("Supplier", back_populates="toys")