"""
Seeds the database with sample suppliers for testing and demos.
Creates suppliers for common toy categories.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.database import engine

print("Seeding suppliers...")

sample_suppliers = [
    {"name": "Action Heroes Inc", "email": "orders@actionheroes.com", "specialty": "Action Figures"},
    {"name": "Plush Paradise", "email": "contact@plushparadise.com", "specialty": "Plush"},
    {"name": "Building Blocks Ltd", "email": "sales@buildingblocks.com", "specialty": "Building"},
    {"name": "DollWorld Inc", "email": "restock@dollworld.com", "specialty": "Dolls"},
    {"name": "Board Game Masters", "email": "info@boardgamemasters.com", "specialty": "Board Games"},
    {"name": "Educational Toys Co", "email": "orders@edutoys.com", "specialty": "Educational"},
    {"name": "Outdoor Play Experts", "email": "contact@outdoorplay.com", "specialty": "Outdoor"},
]

with engine.connect() as conn:
    for supplier in sample_suppliers:
        # Check if supplier already exists
        result = conn.execute(
            text("SELECT id FROM suppliers WHERE name = :name"),
            {"name": supplier["name"]}
        )
        if result.fetchone():
            print(f"⊗ Supplier '{supplier['name']}' already exists, skipping...")
            continue
        
        # Insert supplier
        conn.execute(
            text("""
                INSERT INTO suppliers (name, email, specialty)
                VALUES (:name, :email, :specialty)
            """),
            supplier
        )
        print(f"✓ Created supplier: {supplier['name']} ({supplier['specialty']})")
    
    conn.commit()
    print(f"\n✅ Seeding completed! {len(sample_suppliers)} suppliers ready.")
