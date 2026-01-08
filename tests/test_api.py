import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "ConsumeSafe" in response.json()["message"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_check_boycotted_product():
    """Test checking a boycotted product"""
    response = client.get("/api/check?product_name=Coca-Cola")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "boycotted"
    assert len(data["found_items"]) > 0

def test_check_safe_product():
    """Test checking a safe product"""
    response = client.get("/api/check?product_name=RandomNonExistentProduct123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "safe"

def test_check_product_empty():
    """Test check with empty product name"""
    response = client.get("/api/check?product_name=")
    assert response.status_code == 422  # Validation error

def test_get_alternatives():
    """Test getting alternatives"""
    response = client.get("/api/alternatives?product_name=Nestlé")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_list_boycotts():
    """Test listing all boycotts"""
    response = client.get("/api/boycotts?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["products"]) > 0
    assert data["total"] > 0

def test_list_boycotts_with_category():
    """Test listing boycotts by category"""
    response = client.get("/api/boycotts?category=Beverages")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_list_boycotts_with_intensity():
    """Test listing boycotts by intensity"""
    response = client.get("/api/boycotts?intensity=High")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_get_categories():
    """Test getting categories"""
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0

def test_get_stats():
    """Test getting statistics"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "categories" in data
    assert "by_intensity" in data

def test_search_product():
    """Test search endpoint"""
    response = client.get("/api/search?q=Coca")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data or data["status"] == "no_results"

def test_search_empty():
    """Test search with empty query"""
    response = client.get("/api/search?q=")
    assert response.status_code == 422

def test_get_message():
    """Test getting solidarity message"""
    response = client.get("/api/message")
    assert response.status_code == 200
    assert "message" in response.json()

def test_feedback_submission():
    """Test feedback submission"""
    response = client.post("/api/feedback", json={
        "comment": "Great app!",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_cors_headers():
    """Test CORS headers"""
    response = client.get("/")
    assert response.status_code == 200

def test_multiple_searches():
    """Test multiple sequential searches"""
    products = ["Pepsi", "Starbucks", "HP", "Nestlé"]
    for product in products:
        response = client.get(f"/api/check?product_name={product}")
        assert response.status_code == 200
        assert "status" in response.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
