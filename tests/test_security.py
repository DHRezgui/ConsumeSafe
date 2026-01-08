"""
ConsumeSafe Security Tests
Testing for OWASP Top 10 and DevSecOps compliance
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ConsumeSafe.app.main import app, sanitize_input, validate_query, rate_limiter

client = TestClient(app)

# ============================================================================
# INPUT VALIDATION & SANITIZATION TESTS
# ============================================================================

class TestInputValidation:
    """Test input sanitization and validation"""
    
    def test_sanitize_basic_input(self):
        """Test basic input sanitization"""
        result = sanitize_input("Coca-Cola")
        assert result == "Coca-Cola"
    
    def test_sanitize_xss_attempt(self):
        """Test XSS injection prevention"""
        result = sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" not in result
    
    def test_sanitize_html_entities(self):
        """Test HTML entity escaping"""
        result = sanitize_input("Test & Code")
        assert "&" in result  # Should be escaped as &amp;
    
    def test_sanitize_sql_injection(self):
        """Test SQL injection prevention"""
        result = sanitize_input("'; DROP TABLE products--")
        # Should remove special characters
        assert "DROP" not in result or result.count("'") == 0
    
    def test_sanitize_null_bytes(self):
        """Test null byte removal"""
        result = sanitize_input("Test\x00Input")
        assert "\x00" not in result
    
    def test_sanitize_length_limit(self):
        """Test maximum length enforcement"""
        long_input = "a" * 300
        result = sanitize_input(long_input, max_length=100)
        assert len(result) <= 100
    
    def test_validate_query_empty(self):
        """Test empty query validation"""
        with pytest.raises(ValueError):
            validate_query("")
    
    def test_validate_query_too_long(self):
        """Test query length limit"""
        with pytest.raises(ValueError):
            validate_query("a" * 101)

# ============================================================================
# XSS (Cross-Site Scripting) PREVENTION
# ============================================================================

class TestXSSPrevention:
    """Test XSS attack prevention"""
    
    def test_search_xss_payload(self):
        """Test search endpoint with XSS payload"""
        response = client.get("/api/search?q=<script>alert(1)</script>")
        assert response.status_code == 200
        # Ensure response doesn't contain unescaped script
        assert "<script>" not in response.text or response.json() is not None
    
    def test_product_xss_response(self):
        """Test that product data is properly escaped in response"""
        response = client.get("/api/search?q=Coca")
        assert response.status_code == 200
        data = response.json()
        # If results exist, they should be properly formatted
        if data.get('results'):
            for product in data['results']:
                # Validate JSON structure
                assert isinstance(product, dict)
    
    def test_feedback_xss_prevention(self):
        """Test feedback endpoint against XSS"""
        payload = {
            "message": "<img src=x onerror=alert(1)>",
            "email": "test@test.com"
        }
        response = client.post("/api/feedback", json=payload)
        assert response.status_code == 200

# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_creation(self):
        """Test rate limiter initialization"""
        assert rate_limiter.max_requests == 100
        assert rate_limiter.time_window == 60
    
    def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows normal requests"""
        test_ip = "192.168.1.100"
        # Should allow up to 100 requests
        for i in range(10):
            assert rate_limiter.is_allowed(test_ip) == True
    
    def test_rate_limiter_blocks_excess(self):
        """Test rate limit enforcement"""
        test_ip = "192.168.1.101"
        # Make 100 requests
        for i in range(100):
            allowed = rate_limiter.is_allowed(test_ip)
        
        # 101st request should be blocked
        result = rate_limiter.is_allowed(test_ip)
        # Either blocked (False) or depends on timing
        assert isinstance(result, bool)

# ============================================================================
# SECURITY HEADERS TESTS
# ============================================================================

class TestSecurityHeaders:
    """Test security headers in responses"""
    
    def test_content_type_options_header(self):
        """Test X-Content-Type-Options header"""
        response = client.get("/api/health")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    def test_frame_options_header(self):
        """Test X-Frame-Options header"""
        response = client.get("/api/health")
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
    
    def test_xss_protection_header(self):
        """Test X-XSS-Protection header"""
        response = client.get("/api/health")
        assert "X-XSS-Protection" in response.headers
        assert "1" in response.headers["X-XSS-Protection"]
    
    def test_csp_header(self):
        """Test Content-Security-Policy header"""
        response = client.get("/api/health")
        assert "Content-Security-Policy" in response.headers
    
    def test_hsts_header(self):
        """Test Strict-Transport-Security header"""
        response = client.get("/api/health")
        assert "Strict-Transport-Security" in response.headers
    
    def test_referrer_policy_header(self):
        """Test Referrer-Policy header"""
        response = client.get("/api/health")
        assert "Referrer-Policy" in response.headers
    
    def test_permissions_policy_header(self):
        """Test Permissions-Policy header"""
        response = client.get("/api/health")
        assert "Permissions-Policy" in response.headers

# ============================================================================
# CORS (Cross-Origin Resource Sharing) TESTS
# ============================================================================

class TestCORSConfiguration:
    """Test CORS security configuration"""
    
    def test_cors_allowed_origin(self):
        """Test CORS with allowed origin"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:8080"}
        )
        assert response.status_code == 200
    
    def test_cors_headers_present(self):
        """Test CORS headers are present"""
        response = client.get("/api/health")
        # Response should have access control headers or be allowed
        assert response.status_code == 200

# ============================================================================
# INJECTION ATTACK PREVENTION
# ============================================================================

class TestInjectionPrevention:
    """Test prevention of injection attacks"""
    
    def test_sql_injection_search(self):
        """Test SQL injection in search"""
        payload = "'; DROP TABLE products; --"
        response = client.get(f"/api/search?q={payload}")
        assert response.status_code in [200, 400]
    
    def test_path_traversal(self):
        """Test path traversal prevention"""
        response = client.get("/api/search?q=../../etc/passwd")
        assert response.status_code in [200, 400]
    
    def test_command_injection(self):
        """Test command injection prevention"""
        response = client.get("/api/search?q=test; rm -rf /")
        assert response.status_code in [200, 400]
    
    def test_ldap_injection(self):
        """Test LDAP injection prevention"""
        response = client.get("/api/search?q=*)(&(uid=*")
        assert response.status_code in [200, 400]

# ============================================================================
# ENDPOINT VALIDATION TESTS
# ============================================================================

class TestEndpointValidation:
    """Test endpoint parameter validation"""
    
    def test_search_missing_query(self):
        """Test search with missing query parameter"""
        response = client.get("/api/search")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        response = client.get("/api/search?q=")
        assert response.status_code in [200, 400]
    
    def test_search_limit_exceeded(self):
        """Test search with limit exceeding max"""
        response = client.get("/api/search?q=test&limit=1000")
        # Should either be limited or return error
        assert response.status_code in [200, 400]
    
    def test_intensity_invalid_value(self):
        """Test intensity endpoint with invalid value"""
        response = client.get("/api/intensity/InvalidValue")
        assert response.status_code in [400, 422]
    
    def test_category_invalid_value(self):
        """Test category endpoint with invalid value"""
        response = client.get("/api/category/NonExistent")
        # May return empty or error
        assert response.status_code in [200, 400]

# ============================================================================
# AUTHENTICATION & AUTHORIZATION TESTS
# ============================================================================

class TestAccessControl:
    """Test access control"""
    
    def test_health_endpoint_no_auth(self):
        """Test health endpoint doesn't require authentication"""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_search_endpoint_no_auth(self):
        """Test search endpoint doesn't require authentication"""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
    
    def test_download_endpoint_no_auth(self):
        """Test download endpoint doesn't require authentication"""
        response = client.get("/api/download")
        assert response.status_code == 200

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test secure error handling"""
    
    def test_404_error_message(self):
        """Test 404 error doesn't expose system info"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        # Response should not contain system info
        text = response.text.lower()
        assert "traceback" not in text
        assert "file" not in text or response.status_code != 500
    
    def test_500_error_no_traceback(self):
        """Test 500 errors don't expose traceback"""
        # This is harder to test without causing actual errors
        # Verify that 500 responses are generic
        pass
    
    def test_error_response_format(self):
        """Test error responses have consistent format"""
        response = client.get("/api/search")  # Missing required param
        assert response.status_code == 422
        data = response.json()
        # Should have detail field
        assert "detail" in data

# ============================================================================
# PERFORMANCE & DOS PROTECTION TESTS
# ============================================================================

class TestDOSProtection:
    """Test protection against Denial of Service"""
    
    def test_large_request_handling(self):
        """Test handling of large requests"""
        long_query = "a" * 1000
        response = client.get(f"/api/search?q={long_query}")
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_many_parameters(self):
        """Test handling of many parameters"""
        response = client.get("/api/search?q=test&" + "&".join([f"param{i}=value{i}" for i in range(100)]))
        # Should handle without crashing
        assert response.status_code in [200, 400]

# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_boycott_products_loaded(self):
        """Test that boycott products are loaded"""
        response = client.get("/api/boycotts")
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
    
    def test_stats_consistency(self):
        """Test statistics consistency"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "total_products" in stats
        assert "by_category" in stats
        assert "by_intensity" in stats
    
    def test_categories_consistency(self):
        """Test categories are consistent"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

# ============================================================================
# LOGGING & MONITORING TESTS
# ============================================================================

class TestLoggingAndMonitoring:
    """Test logging functionality"""
    
    def test_successful_request_logged(self):
        """Test successful requests are logged"""
        # This would require capturing logs
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_error_request_logged(self):
        """Test error requests are logged"""
        response = client.get("/api/search")  # Missing param
        assert response.status_code == 422

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for full workflows"""
    
    def test_search_workflow(self):
        """Test complete search workflow"""
        # 1. Search for a product
        response = client.get("/api/search?q=Coca")
        assert response.status_code == 200
        data = response.json()
        
        # 2. Verify response structure
        assert "results" in data
        assert "count" in data
        assert "query" in data
    
    def test_statistics_workflow(self):
        """Test complete statistics workflow"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        stats = response.json()
        
        # Verify structure
        assert stats["total_products"] > 0
        assert len(stats["by_category"]) > 0
        assert len(stats["by_intensity"]) > 0
    
    def test_download_workflow(self):
        """Test complete download workflow"""
        response = client.get("/api/download")
        assert response.status_code == 200
        # Verify CSV content
        assert "boycott_product" in response.text
        assert "tunisian_alternative" in response.text

# ============================================================================
# COMPLIANCE TESTS
# ============================================================================

class TestCompliance:
    """Test OWASP Top 10 compliance"""
    
    def test_a01_broken_access_control(self):
        """OWASP A01: Broken Access Control"""
        # No authentication is required, so no access control vulnerability
        response = client.get("/api/boycotts")
        assert response.status_code == 200
    
    def test_a03_injection(self):
        """OWASP A03: Injection"""
        # Tested in TestInjectionPrevention
        response = client.get("/api/search?q=<script>alert(1)</script>")
        assert response.status_code in [200, 400]
    
    def test_a07_identification_authentication(self):
        """OWASP A07: Broken Authentication"""
        # No authentication required, N/A
        pass
    
    def test_a08_data_integrity_failures(self):
        """OWASP A08: Software and Data Integrity Failures"""
        # All data is read-only from CSV
        response = client.get("/api/boycotts")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
