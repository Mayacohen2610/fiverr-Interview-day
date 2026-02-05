"""
Pytest tests for API endpoints using FastAPI TestClient.
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
    """Tests that each toy in GET /toys has the expected fields."""
    response = client.get("/toys")
    assert response.status_code == 200
    toys = response.json()
    for toy in toys:
        assert "id" in toy
        assert "toy_name" in toy
        assert "category" in toy
        assert "price" in toy
        assert "in_stock" in toy


def test_post_toy_and_get():
    """Tests creating a toy via POST /toys and fetching it via GET /toys."""
    new_toy = {
        "toy_name": "Test Toy",
        "category": "Test Category",
        "price": 9.99,
        "in_stock": True,
    }
    response = client.post("/toys", json=new_toy)
    assert response.status_code == 200
    created = response.json()
    assert created["toy_name"] == new_toy["toy_name"]
    assert created["category"] == new_toy["category"]
    assert created["price"] == new_toy["price"]
    assert created["in_stock"] == new_toy["in_stock"]
    assert "id" in created
