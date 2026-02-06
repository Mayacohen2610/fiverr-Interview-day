"""
Pytest tests for supplier specialty validation (the "Specialty Rule").
Tests both application-level and database-level validation.
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_toy_with_nonexistent_supplier():
    """Tests that creating a toy with non-existent supplier fails."""
    toy = {
        "toy_name": "Orphan Toy",
        "category": "Action Figures",
        "price": 25.99,
        "supplier_id": 999999
    }
    response = client.post("/toys", json=toy)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"].lower()


def test_create_toy_with_mismatched_specialty():
    """Tests that creating a toy with mismatched supplier specialty fails."""
    # Create a supplier with "Dolls" specialty
    supplier = {
        "name": "Dolls Only Supplier",
        "email": "dolls@supplier.com",
        "specialty": "Dolls"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Try to create an "Action Figures" toy with this supplier
    toy = {
        "toy_name": "Mismatched Action Figure",
        "category": "Action Figures",
        "price": 29.99,
        "supplier_id": supplier_id
    }
    response = client.post("/toys", json=toy)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "specialty" in detail.lower()
    assert "does not match" in detail.lower()


def test_create_toy_with_matching_specialty():
    """Tests that creating a toy with matching supplier specialty succeeds."""
    # Create a supplier with "Building" specialty
    supplier = {
        "name": "Building Blocks Supplier",
        "email": "building@supplier.com",
        "specialty": "Building"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create a "Building" toy with this supplier
    toy = {
        "toy_name": "Lego-like Set",
        "category": "Building",
        "price": 49.99,
        "supplier_id": supplier_id
    }
    response = client.post("/toys", json=toy)
    assert response.status_code == 200
    data = response.json()
    assert data["toy_name"] == toy["toy_name"]
    assert data["supplier_id"] == supplier_id


def test_update_toy_supplier_with_mismatch():
    """Tests that updating a toy's supplier to mismatched specialty fails."""
    # Create two suppliers with different specialties
    supplier1 = {
        "name": "Plush Supplier",
        "email": "plush@supplier.com",
        "specialty": "Plush"
    }
    supplier2 = {
        "name": "Educational Supplier",
        "email": "educational@supplier.com",
        "specialty": "Educational"
    }
    s1_response = client.post("/suppliers", json=supplier1)
    s2_response = client.post("/suppliers", json=supplier2)
    assert s1_response.status_code == 200
    assert s2_response.status_code == 200
    supplier1_id = s1_response.json()["id"]
    supplier2_id = s2_response.json()["id"]
    
    # Create a Plush toy with supplier1
    toy = {
        "toy_name": "Teddy Bear",
        "category": "Plush",
        "price": 19.99,
        "supplier_id": supplier1_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Try to update to supplier2 (Educational) - should fail
    update = {"supplier_id": supplier2_id}
    response = client.patch(f"/toys/{toy_id}", json=update)
    assert response.status_code == 400
    assert "specialty" in response.json()["detail"].lower()


def test_update_toy_supplier_with_match():
    """Tests that updating a toy's supplier to matching specialty succeeds."""
    # Create two suppliers with the same specialty
    supplier1 = {
        "name": "Outdoor Supplier A",
        "email": "outdoorA@supplier.com",
        "specialty": "Outdoor"
    }
    supplier2 = {
        "name": "Outdoor Supplier B",
        "email": "outdoorB@supplier.com",
        "specialty": "Outdoor"
    }
    s1_response = client.post("/suppliers", json=supplier1)
    s2_response = client.post("/suppliers", json=supplier2)
    assert s1_response.status_code == 200
    assert s2_response.status_code == 200
    supplier1_id = s1_response.json()["id"]
    supplier2_id = s2_response.json()["id"]
    
    # Create an Outdoor toy with supplier1
    toy = {
        "toy_name": "Soccer Ball",
        "category": "Outdoor",
        "price": 15.99,
        "supplier_id": supplier1_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    toy_id = toy_response.json()["id"]
    
    # Update to supplier2 (also Outdoor) - should succeed
    update = {"supplier_id": supplier2_id}
    response = client.patch(f"/toys/{toy_id}", json=update)
    assert response.status_code == 200
    assert response.json()["supplier_id"] == supplier2_id


def test_cannot_delete_supplier_with_toys():
    """Tests that deleting a supplier with toys is blocked."""
    # Create a supplier
    supplier = {
        "name": "Supplier With Toys",
        "email": "withtoys@supplier.com",
        "specialty": "Board Games"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create a toy with this supplier
    toy = {
        "toy_name": "Chess Set",
        "category": "Board Games",
        "price": 35.00,
        "supplier_id": supplier_id
    }
    toy_response = client.post("/toys", json=toy)
    assert toy_response.status_code == 200
    
    # Try to delete the supplier - should fail
    response = client.delete(f"/suppliers/{supplier_id}")
    assert response.status_code == 409
    assert "cannot delete" in response.json()["detail"].lower()


def test_category_normalization_matches():
    """Tests that category normalization ensures specialty matching works."""
    # Create supplier with title case specialty
    supplier = {
        "name": "Case Sensitive Test",
        "email": "case@supplier.com",
        "specialty": "Action Figures"  # Title case
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Create toy with lowercase category (should be normalized)
    toy = {
        "toy_name": "Hero Figure",
        "category": "action figures",  # lowercase
        "price": 24.99,
        "supplier_id": supplier_id
    }
    response = client.post("/toys", json=toy)
    assert response.status_code == 200
    # Both get normalized to "Action Figures", so they should match
