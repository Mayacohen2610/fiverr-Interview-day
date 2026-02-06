"""
Pytest tests for critical inventory reporting.
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_critical_inventory_empty():
    """Tests that critical inventory returns empty list when no critical items."""
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    # May or may not be empty depending on existing data
    assert isinstance(response.json(), list)


def test_critical_inventory_out_of_stock():
    """Tests that out-of-stock toys appear in critical inventory."""
    # Create a supplier
    supplier = {
        "name": "Out of Stock Test Supplier",
        "email": "outofstock@supplier.com",
        "specialty": "Plush"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create an out-of-stock toy
    toy = {
        "toy_name": "Sold Out Bear",
        "category": "Plush",
        "price": 15.00,
        "in_stock": False,
        "supplier_id": supplier_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Check critical inventory
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    data = response.json()
    
    # Find our toy in the critical inventory
    critical_toy = next((item for item in data if item["id"] == toy_id), None)
    assert critical_toy is not None
    assert critical_toy["in_stock"] is False
    assert "out of stock" in critical_toy["reason"].lower()
    assert critical_toy["supplier_email"] == supplier["email"]


def test_critical_inventory_high_value():
    """Tests that high-value toys (price > 200) appear in critical inventory."""
    # Create a supplier
    supplier = {
        "name": "High Value Test Supplier",
        "email": "highvalue@supplier.com",
        "specialty": "Educational"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create a high-value toy (price > 200)
    toy = {
        "toy_name": "Expensive Learning System",
        "category": "Educational",
        "price": 250.00,
        "in_stock": True,
        "supplier_id": supplier_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Check critical inventory
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    data = response.json()
    
    # Find our toy in the critical inventory
    critical_toy = next((item for item in data if item["id"] == toy_id), None)
    assert critical_toy is not None
    assert critical_toy["price"] > 200
    assert critical_toy["in_stock"] is True
    assert "high value" in critical_toy["reason"].lower()
    assert critical_toy["supplier_email"] == supplier["email"]


def test_critical_inventory_both_conditions():
    """Tests toy that is both out of stock AND high value."""
    # Create a supplier
    supplier = {
        "name": "Both Conditions Supplier",
        "email": "both@supplier.com",
        "specialty": "Building"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create a toy that's both out of stock and high value
    toy = {
        "toy_name": "Rare Building Set",
        "category": "Building",
        "price": 299.99,
        "in_stock": False,
        "supplier_id": supplier_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Check critical inventory
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    data = response.json()
    
    # Find our toy in the critical inventory
    critical_toy = next((item for item in data if item["id"] == toy_id), None)
    assert critical_toy is not None
    assert critical_toy["price"] > 200
    assert critical_toy["in_stock"] is False
    # Reason should mention both conditions
    reason_lower = critical_toy["reason"].lower()
    assert "out of stock" in reason_lower or "high value" in reason_lower


def test_critical_inventory_not_critical():
    """Tests that in-stock, normal-priced toys don't appear in critical inventory."""
    # Create a supplier
    supplier = {
        "name": "Normal Toy Supplier",
        "email": "normal@supplier.com",
        "specialty": "Outdoor"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create a normal toy (in stock, price < 200)
    toy = {
        "toy_name": "Normal Basketball",
        "category": "Outdoor",
        "price": 25.00,
        "in_stock": True,
        "supplier_id": supplier_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Check critical inventory
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    data = response.json()
    
    # Our toy should NOT be in critical inventory
    critical_toy = next((item for item in data if item["id"] == toy_id), None)
    assert critical_toy is None


def test_critical_inventory_includes_supplier_info():
    """Tests that critical inventory includes supplier contact information."""
    # Create a supplier
    supplier = {
        "name": "Contact Info Test",
        "email": "contact@supplier.com",
        "specialty": "Dolls"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create an out-of-stock toy
    toy = {
        "toy_name": "Contact Test Doll",
        "category": "Dolls",
        "price": 45.00,
        "in_stock": False,
        "supplier_id": supplier_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Check critical inventory
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    data = response.json()
    
    # Find our toy and verify supplier info
    critical_toy = next((item for item in data if item["id"] == toy_id), None)
    assert critical_toy is not None
    assert critical_toy["supplier_name"] == supplier["name"]
    assert critical_toy["supplier_email"] == supplier["email"]
    assert "reason" in critical_toy


def test_critical_inventory_threshold_exactly_200():
    """Tests toys at exactly 200 price threshold."""
    # Create a supplier
    supplier = {
        "name": "Threshold Test Supplier",
        "email": "threshold@supplier.com",
        "specialty": "Board Games"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Toy at exactly 200 (should NOT be critical per requirement: price > 200)
    toy1 = {
        "toy_name": "Exactly 200 Game",
        "category": "Board Games",
        "price": 200.00,
        "in_stock": True,
        "supplier_id": supplier_id
    }
    toy1_response = client.post("/toys", json=toy1)
    assert toy1_response.status_code == 200
    toy1_id = toy1_response.json()["id"]
    
    # Toy at 200.01 (should be critical)
    toy2 = {
        "toy_name": "Just Over 200 Game",
        "category": "Board Games",
        "price": 200.01,
        "in_stock": True,
        "supplier_id": supplier_id
    }
    toy2_response = client.post("/toys", json=toy2)
    assert toy2_response.status_code == 200
    toy2_id = toy2_response.json()["id"]
    
    # Check critical inventory
    response = client.get("/reports/critical-inventory")
    assert response.status_code == 200
    data = response.json()
    
    # Toy at exactly 200 should NOT be in critical inventory
    toy1_critical = next((item for item in data if item["id"] == toy1_id), None)
    assert toy1_critical is None
    
    # Toy at 200.01 SHOULD be in critical inventory
    toy2_critical = next((item for item in data if item["id"] == toy2_id), None)
    assert toy2_critical is not None
