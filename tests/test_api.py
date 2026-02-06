"""
Pytest tests for API endpoints using FastAPI TestClient.
Updated to work with supplier module requirements.
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Tests the /health endpoint returns status up or down."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("up", "down")


def test_get_toys_returns_list():
    """Tests the GET /toys endpoint returns a list."""
    response = client.get("/toys")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_toys_structure():
    """Tests that each toy in GET /toys has the expected fields including supplier info."""
    response = client.get("/toys")
    assert response.status_code == 200
    toys = response.json()
    for toy in toys:
        assert "id" in toy
        assert "toy_name" in toy
        assert "category" in toy
        assert "price" in toy
        assert "in_stock" in toy
        assert "supplier_id" in toy
        # supplier can be None for toys without assigned suppliers
        if toy["supplier_id"] is not None:
            assert "supplier" in toy


def test_post_toy_with_supplier():
    """Tests creating a toy with a supplier via POST /toys."""
    # First create a supplier
    supplier = {
        "name": "Test API Supplier",
        "email": "testapi@supplier.com",
        "specialty": "Test Category"
    }
    supplier_response = client.post("/suppliers", json=supplier)
    assert supplier_response.status_code == 200
    supplier_id = supplier_response.json()["id"]
    
    # Now create a toy with this supplier
    new_toy = {
        "toy_name": "Test Toy",
        "category": "Test Category",
        "price": 9.99,
        "in_stock": True,
        "supplier_id": supplier_id
    }
    response = client.post("/toys", json=new_toy)
    assert response.status_code == 200
    created = response.json()
    assert created["toy_name"] == new_toy["toy_name"]
    assert created["category"] == new_toy["category"]
    assert created["price"] == new_toy["price"]
    assert created["in_stock"] == new_toy["in_stock"]
    assert created["supplier_id"] == supplier_id
    assert "id" in created


def test_post_toy_without_supplier_fails():
    """Tests that creating a toy without supplier_id fails with validation error."""
    new_toy = {
        "toy_name": "Toy Without Supplier",
        "category": "Test Category",
        "price": 15.99,
        "in_stock": True
        # Missing supplier_id
    }
    response = client.post("/toys", json=new_toy)
    assert response.status_code == 422  # Pydantic validation error


def test_post_toy_with_nonexistent_supplier_fails():
    """Tests that creating a toy with non-existent supplier fails."""
    new_toy = {
        "toy_name": "Toy With Bad Supplier",
        "category": "Test Category",
        "price": 19.99,
        "in_stock": True,
        "supplier_id": 999999  # Non-existent supplier
    }
    response = client.post("/toys", json=new_toy)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"].lower()