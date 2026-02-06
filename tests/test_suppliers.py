"""
Pytest tests for supplier CRUD operations.
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_supplier():
    """Tests creating a supplier with valid data."""
    supplier = {
        "name": "Test Supplier Ltd",
        "email": "test@supplier.com",
        "specialty": "Action Figures"
    }
    response = client.post("/suppliers", json=supplier)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == supplier["name"]
    assert data["email"] == supplier["email"]
    assert data["specialty"] == supplier["specialty"]
    assert "id" in data


def test_create_supplier_invalid_email():
    """Tests that invalid email format is rejected."""
    supplier = {
        "name": "Bad Email Supplier",
        "email": "not-an-email",
        "specialty": "Plush"
    }
    response = client.post("/suppliers", json=supplier)
    assert response.status_code == 422  # Pydantic validation error


def test_create_supplier_duplicate_name():
    """Tests that duplicate supplier names are rejected."""
    supplier = {
        "name": "Unique Name Supplier",
        "email": "unique1@supplier.com",
        "specialty": "Building"
    }
    # Create first supplier
    response1 = client.post("/suppliers", json=supplier)
    assert response1.status_code == 200
    
    # Try to create duplicate
    supplier["email"] = "unique2@supplier.com"  # Different email
    response2 = client.post("/suppliers", json=supplier)
    assert response2.status_code == 409  # Conflict


def test_get_all_suppliers():
    """Tests retrieving all suppliers."""
    response = client.get("/suppliers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_supplier_by_id():
    """Tests retrieving a single supplier by id."""
    # Create a supplier first
    supplier = {
        "name": "Get By ID Test Supplier",
        "email": "getbyid@supplier.com",
        "specialty": "Dolls"
    }
    create_response = client.post("/suppliers", json=supplier)
    assert create_response.status_code == 200
    supplier_id = create_response.json()["id"]
    
    # Get the supplier
    response = client.get(f"/suppliers/{supplier_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == supplier_id
    assert data["name"] == supplier["name"]
    assert "toy_count" in data


def test_get_nonexistent_supplier():
    """Tests that getting a nonexistent supplier returns 404."""
    response = client.get("/suppliers/999999")
    assert response.status_code == 404


def test_update_supplier():
    """Tests partially updating a supplier."""
    # Create a supplier
    supplier = {
        "name": "Update Test Supplier",
        "email": "update@supplier.com",
        "specialty": "Educational"
    }
    create_response = client.post("/suppliers", json=supplier)
    assert create_response.status_code == 200
    supplier_id = create_response.json()["id"]
    
    # Update email only
    update = {"email": "newemail@supplier.com"}
    response = client.patch(f"/suppliers/{supplier_id}", json=update)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newemail@supplier.com"
    assert data["name"] == supplier["name"]  # Unchanged


def test_update_supplier_invalid_email():
    """Tests that updating to an invalid email is rejected."""
    # Create a supplier
    supplier = {
        "name": "Email Update Test",
        "email": "valid@supplier.com",
        "specialty": "Outdoor"
    }
    create_response = client.post("/suppliers", json=supplier)
    assert create_response.status_code == 200
    supplier_id = create_response.json()["id"]
    
    # Try to update with invalid email
    update = {"email": "not-valid-email"}
    response = client.patch(f"/suppliers/{supplier_id}", json=update)
    assert response.status_code == 422  # Pydantic validation error


def test_delete_supplier_without_toys():
    """Tests deleting a supplier that has no toys."""
    # Create a supplier
    supplier = {
        "name": "Delete Test Supplier",
        "email": "delete@supplier.com",
        "specialty": "Board Games"
    }
    create_response = client.post("/suppliers", json=supplier)
    assert create_response.status_code == 200
    supplier_id = create_response.json()["id"]
    
    # Delete the supplier
    response = client.delete(f"/suppliers/{supplier_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/suppliers/{supplier_id}")
    assert get_response.status_code == 404


def test_category_normalization_in_specialty():
    """Tests that category values are normalized to title case."""
    supplier = {
        "name": "Normalization Test",
        "email": "normalize@supplier.com",
        "specialty": "action figures"  # lowercase
    }
    response = client.post("/suppliers", json=supplier)
    assert response.status_code == 200
    data = response.json()
    assert data["specialty"] == "Action Figures"  # Title case
