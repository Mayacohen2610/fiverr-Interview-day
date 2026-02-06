"""
Creates the suppliers table and adds supplier integration to the toys table.
This migration script:
- Creates suppliers table with email validation
- Adds supplier_id column to toys table (nullable for existing data)
- Creates foreign key constraint with ON DELETE RESTRICT
- Creates trigger function and trigger for specialty validation
- Creates critical_inventory_view for reporting

Run this script once to set up the supplier module.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.database import engine

print("Starting supplier module migration...")

with engine.connect() as conn:
    # 1. Create suppliers table with email CHECK constraint
    print("Creating suppliers table...")
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
            specialty VARCHAR(255) NOT NULL
        )
    """))
    print("✓ Suppliers table created")

    # 2. Add supplier_id column to toys table (nullable for existing data)
    print("Adding supplier_id column to toys table...")
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'toys' AND column_name = 'supplier_id'
            ) THEN
                ALTER TABLE toys ADD COLUMN supplier_id INTEGER;
            END IF;
        END $$;
    """))
    print("✓ supplier_id column added")

    # 3. Add foreign key constraint
    print("Creating foreign key constraint...")
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'fk_toys_supplier' AND table_name = 'toys'
            ) THEN
                ALTER TABLE toys 
                ADD CONSTRAINT fk_toys_supplier 
                FOREIGN KEY (supplier_id) 
                REFERENCES suppliers(id) 
                ON DELETE RESTRICT;
            END IF;
        END $$;
    """))
    print("✓ Foreign key constraint created")

    # 4. Create trigger function for specialty validation
    print("Creating specialty validation trigger function...")
    conn.execute(text("""
        CREATE OR REPLACE FUNCTION validate_supplier_specialty()
        RETURNS TRIGGER AS $$
        DECLARE
            supplier_specialty VARCHAR(255);
        BEGIN
            -- Only validate if supplier_id is not NULL
            IF NEW.supplier_id IS NOT NULL THEN
                -- Get the supplier's specialty
                SELECT specialty INTO supplier_specialty
                FROM suppliers
                WHERE id = NEW.supplier_id;
                
                -- Check if specialty matches category
                IF supplier_specialty IS NULL THEN
                    RAISE EXCEPTION 'Supplier with id % does not exist', NEW.supplier_id;
                END IF;
                
                IF supplier_specialty != NEW.category THEN
                    RAISE EXCEPTION 'Supplier specialty "%" does not match toy category "%". A supplier can only provide toys in their specialty category.',
                        supplier_specialty, NEW.category;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))
    print("✓ Trigger function created")

    # 5. Create trigger
    print("Creating specialty validation trigger...")
    conn.execute(text("""
        DROP TRIGGER IF EXISTS validate_supplier_specialty_trigger ON toys;
        
        CREATE TRIGGER validate_supplier_specialty_trigger
        BEFORE INSERT OR UPDATE ON toys
        FOR EACH ROW
        EXECUTE FUNCTION validate_supplier_specialty();
    """))
    print("✓ Trigger created")

    # 6. Create critical inventory view
    print("Creating critical_inventory_view...")
    conn.execute(text("""
        CREATE OR REPLACE VIEW critical_inventory_view AS
        SELECT 
            t.id,
            t.toy_name,
            t.category,
            t.price,
            t.in_stock,
            s.name as supplier_name,
            s.email as supplier_email,
            CASE 
                WHEN NOT t.in_stock AND t.price > 200 THEN 'Out of Stock, High Value Item'
                WHEN NOT t.in_stock THEN 'Out of Stock'
                WHEN t.price > 200 THEN 'High Value Item'
            END as reason
        FROM toys t
        LEFT JOIN suppliers s ON t.supplier_id = s.id
        WHERE NOT t.in_stock OR t.price > 200
        ORDER BY t.in_stock ASC, t.price DESC;
    """))
    print("✓ Critical inventory view created")

    # Commit all changes
    conn.commit()
    print("\n✅ Supplier module migration completed successfully!")
    print("\nNext steps:")
    print("1. Create suppliers using POST /suppliers endpoint")
    print("2. Assign suppliers to existing toys (supplier_id is nullable)")
    print("3. New toys will require a valid supplier_id")
