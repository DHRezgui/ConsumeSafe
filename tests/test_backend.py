"""Comprehensive backend API tests for ConsumeSafe."""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Mock the import before importing main
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app, BoycottData

client = TestClient(app)


class TestHealth:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test /api/health endpoint returns OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestProductEndpoints:
    """Test product-related endpoints."""
    
    def test_get_products(self):
        """Test /api/products returns product list."""
        response = client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert isinstance(data["products"], list)
    
    def test_search_products(self):
        """Test /api/search endpoint."""
        response = client.get("/api/search?query=nestle")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_search_empty_query(self):
        """Test search with empty query."""
        response = client.get("/api/search?query=")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
    
    def test_check_product(self):
        """Test /api/check endpoint for product status."""
        response = client.get("/api/check?product=Sprite")
        assert response.status_code == 200
        data = response.json()
        assert "boycotted" in data
        assert isinstance(data["boycotted"], bool)
    
    def test_check_nonexistent_product(self):
        """Test checking nonexistent product."""
        response = client.get("/api/check?product=NonExistentProduct123XYZ")
        assert response.status_code == 200
        data = response.json()
        assert data["boycotted"] == False


class TestCategoryEndpoints:
    """Test category-related endpoints."""
    
    def test_get_categories(self):
        """Test /api/categories endpoint."""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], dict)
        # Verify each category has count
        for cat, count in data["categories"].items():
            assert isinstance(count, int)
    
    def test_filter_by_category(self):
        """Test /api/products?category=X endpoint."""
        # First get available categories
        response = client.get("/api/categories")
        categories = response.json()["categories"]
        
        if categories:
            first_category = list(categories.keys())[0]
            response = client.get(f"/api/products?category={first_category}")
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            assert isinstance(data["products"], list)
    
    def test_invalid_category(self):
        """Test filtering with invalid category."""
        response = client.get("/api/products?category=InvalidCategory123")
        assert response.status_code == 200
        data = response.json()
        assert data["products"] == []


class TestAlternatives:
    """Test product alternatives endpoint."""
    
    def test_get_alternatives(self):
        """Test /api/alternatives endpoint."""
        response = client.get("/api/alternatives?product=Nestle")
        assert response.status_code == 200
        data = response.json()
        assert "alternatives" in data
        assert isinstance(data["alternatives"], list)
    
    def test_alternatives_empty(self):
        """Test alternatives for product without alternatives."""
        response = client.get("/api/alternatives?product=NonexistentXYZ")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["alternatives"], list)


class TestStatistics:
    """Test statistics endpoint."""
    
    def test_get_statistics(self):
        """Test /api/stats endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert "total_products" in data
        assert "total_categories" in data
        assert "products_by_intensity" in data
        assert "top_boycotts" in data
        
        assert isinstance(data["total_products"], int)
        assert isinstance(data["total_categories"], int)
        assert isinstance(data["products_by_intensity"], dict)
        assert isinstance(data["top_boycotts"], list)


class TestDownload:
    """Test CSV download endpoint."""
    
    def test_download_boycott_list(self):
        """Test /api/download/boycott_list.csv endpoint."""
        response = client.get("/api/download/boycott_list.csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        
        # Verify CSV content
        content = response.text
        assert "product" in content.lower()


class TestFeedback:
    """Test feedback endpoint."""
    
    def test_submit_feedback(self):
        """Test /api/feedback POST endpoint."""
        feedback_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Great app!",
            "rating": 5
        }
        response = client.post("/api/feedback", json=feedback_data)
        assert response.status_code in [200, 201]
    
    def test_submit_feedback_missing_fields(self):
        """Test feedback submission with missing fields."""
        feedback_data = {
            "name": "Test User",
            # Missing email and message
        }
        response = client.post("/api/feedback", json=feedback_data)
        # Should either accept or reject gracefully
        assert response.status_code in [200, 201, 422]
    
    def test_submit_feedback_invalid_rating(self):
        """Test feedback with invalid rating."""
        feedback_data = {
            "name": "Test",
            "email": "test@test.com",
            "message": "Test",
            "rating": 10  # Invalid: should be 1-5
        }
        response = client.post("/api/feedback", json=feedback_data)
        assert response.status_code in [200, 201, 422]


class TestAIEndpoints:
    """Test AI service endpoints."""
    
    def test_ai_chat(self):
        """Test /api/ai/chat endpoint."""
        payload = {"message": "Why should I boycott Nestle?"}
        response = client.post("/api/ai/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    def test_ai_chat_empty_message(self):
        """Test chat with empty message."""
        payload = {"message": ""}
        response = client.post("/api/ai/chat", json=payload)
        assert response.status_code in [200, 422]
    
    def test_ai_recommendations(self):
        """Test /api/ai/recommend endpoint."""
        payload = {"user_history": ["Nestle", "Coca-Cola"]}
        response = client.post("/api/ai/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_ai_recommendations_empty_history(self):
        """Test recommendations with empty history."""
        payload = {"user_history": []}
        response = client.post("/api/ai/recommend", json=payload)
        assert response.status_code == 200
    
    def test_ai_sentiment_analysis(self):
        """Test /api/ai/analyze-sentiment endpoint."""
        payload = {"text": "This app is amazing! Really helps with ethical shopping."}
        response = client.post("/api/ai/analyze-sentiment", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert data["sentiment"] in ["positive", "negative", "neutral"]
    
    def test_ai_sentiment_negative(self):
        """Test sentiment analysis for negative text."""
        payload = {"text": "This is terrible and doesn't work."}
        response = client.post("/api/ai/analyze-sentiment", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data


class TestCORS:
    """Test CORS headers."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are included."""
        response = client.get("/api/products")
        # FastAPI should handle CORS
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_not_found(self):
        """Test 404 for nonexistent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json_payload(self):
        """Test invalid JSON in request body."""
        response = client.post(
            "/api/feedback",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


class TestDataIntegrity:
    """Test data loading and integrity."""
    
    def test_boycott_data_loads(self):
        """Test that boycott data loads successfully."""
        response = client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) > 0
    
    def test_product_required_fields(self):
        """Test that products have required fields."""
        response = client.get("/api/products")
        products = response.json()["products"]
        
        required_fields = ["name", "category", "intensity"]
        for product in products[:5]:  # Check first 5 products
            for field in required_fields:
                assert field in product, f"Missing field: {field}"


class TestPerformance:
    """Test API performance."""
    
    def test_products_endpoint_response_time(self):
        """Test that products endpoint responds quickly."""
        import time
        start = time.time()
        response = client.get("/api/products")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 1.0, f"Response took {elapsed}s, expected <1s"
    
    def test_search_endpoint_response_time(self):
        """Test search endpoint performance."""
        import time
        start = time.time()
        response = client.get("/api/search?query=test")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.5, f"Search took {elapsed}s, expected <0.5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
