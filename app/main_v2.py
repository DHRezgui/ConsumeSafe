from fastapi import FastAPI, HTTPException, Query, Request, RateLimiter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import csv
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json
import html
import re
from functools import lru_cache
import time
from collections import defaultdict
from threading import Lock

# ============================================================================
# SECURITY & LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security: Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_id: str) -> bool:
        with self.lock:
            now = time.time()
            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < self.time_window
            ]
            
            if len(self.requests[client_id]) >= self.max_requests:
                return False
            
            self.requests[client_id].append(now)
            return True

rate_limiter = RateLimiter(max_requests=100, time_window=60)

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="ConsumeSafe API",
    description="Secure API to check boycotted products and find Tunisian alternatives",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================================
# MIDDLEWARE - SECURITY & PERFORMANCE
# ============================================================================

# 1. Trusted Host Middleware (prevent host header attacks)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "127.0.0.1:*", "*.local"]
)

# 2. GZIP Compression Middleware (performance optimization)
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# 3. CORS Middleware (secure origin policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080", "http://localhost:*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=3600
)

# 4. Custom security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting check
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    # Log requests
    logger.info(f"{request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.tailwindcss.com cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.tailwindcss.com; img-src 'self' data: https:;"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cache-Control"] = "public, max-age=3600"
    
    return response

# ============================================================================
# INPUT VALIDATION & SANITIZATION
# ============================================================================

def sanitize_input(text: str, max_length: int = 200) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Limit length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # HTML escape
    text = html.escape(text)
    
    # Allow only alphanumeric, spaces, hyphens, and parentheses
    text = re.sub(r'[^a-zA-Z0-9\s\-\(\)é\è\ê\ô\ù\â\ä\ö\ü]', '', text)
    
    return text.strip()

def validate_query(query: str) -> str:
    """Validate and sanitize search query"""
    if not query or len(query) < 1:
        raise ValueError("Query cannot be empty")
    if len(query) > 100:
        raise ValueError("Query too long (max 100 characters)")
    return sanitize_input(query, 100)

# ============================================================================
# DATA MODELS & LOADING
# ============================================================================

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'boycott_products.csv')

class BoycottData:
    """Manages boycott products data with caching"""
    
    def __init__(self):
        self.products = []
        self.categories_cache = []
        self.stats_cache = None
        self.last_load = None
        self.load_data()
    
    def load_data(self):
        """Load boycott products dataset from CSV"""
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.products = [dict(row) for row in reader]
            
            # Validate data
            if not self.products:
                raise ValueError("Dataset is empty")
            
            self.last_load = datetime.now()
            logger.info(f"✅ Loaded {len(self.products)} boycott products from {DATA_PATH}")
            
        except FileNotFoundError:
            logger.error(f"❌ Dataset file not found: {DATA_PATH}")
            self.products = []
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            self.products = []
    
    def search_products(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search products by name or brand with relevance ranking"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            name = product.get('boycott_product', '').lower()
            brand = product.get('brand', '').lower()
            
            relevance = 0
            if query_lower == name:
                relevance = 3  # Exact match on name
            elif query_lower == brand:
                relevance = 2  # Exact match on brand
            elif query_lower in name:
                relevance = 1  # Partial match on name
            elif query_lower in brand:
                relevance = 0.5  # Partial match on brand
            
            if relevance > 0:
                product_copy = product.copy()
                product_copy['relevance'] = relevance
                results.append(product_copy)
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:limit]
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category"""
        category_lower = sanitize_input(category).lower()
        return [p for p in self.products 
                if p.get('category', '').lower() == category_lower]
    
    def get_by_intensity(self, intensity: str) -> List[Dict[str, Any]]:
        """Get products by intensity"""
        valid_intensities = ['High', 'Medium', 'Low']
        intensity_clean = sanitize_input(intensity)
        
        if intensity_clean not in valid_intensities:
            raise ValueError(f"Invalid intensity. Must be one of: {', '.join(valid_intensities)}")
        
        return [p for p in self.products 
                if p.get('intensity', '') == intensity_clean]
    
    def get_categories(self) -> List[str]:
        """Get unique categories with caching"""
        if not self.categories_cache:
            categories = set()
            for product in self.products:
                cat = product.get('category', '').strip()
                if cat:
                    categories.add(cat)
            self.categories_cache = sorted(list(categories))
        return self.categories_cache
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics with caching"""
        if self.stats_cache:
            return self.stats_cache
        
        intensity_count = {}
        category_count = {}
        
        for product in self.products:
            intensity = product.get('intensity', 'Unknown')
            category = product.get('category', 'Unknown')
            
            intensity_count[intensity] = intensity_count.get(intensity, 0) + 1
            category_count[category] = category_count.get(category, 0) + 1
        
        self.stats_cache = {
            'total_products': len(self.products),
            'categories': len(self.get_categories()),
            'by_intensity': intensity_count,
            'by_category': category_count,
            'last_updated': datetime.now().isoformat()
        }
        
        return self.stats_cache

# Initialize data
boycott_data = BoycottData()

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 ConsumeSafe API starting up...")
    global boycott_data
    boycott_data = BoycottData()
    logger.info("✅ ConsumeSafe API initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 ConsumeSafe API shutting down...")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "ConsumeSafe API - Stand with Palestine 🇵🇸",
        "version": "2.0.0",
        "status": "healthy",
        "endpoints": {
            "check_product": "/api/check?product_name={name}",
            "search": "/api/search?q={query}",
            "boycotts_list": "/api/boycotts",
            "categories": "/api/categories",
            "by_category": "/api/category/{category}",
            "by_intensity": "/api/intensity/{intensity}",
            "statistics": "/api/stats",
            "health": "/api/health",
            "download": "/api/download"
        },
        "documentation": "/api/docs"
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint with detailed status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "products_loaded": len(boycott_data.products),
        "uptime": datetime.now().isoformat()
    }

# Check product endpoint
@app.get("/api/check")
async def check_product(product_name: str = Query(..., min_length=1, max_length=100)):
    """Check if a product is on the boycott list"""
    try:
        product_name = sanitize_input(product_name)
        
        if not boycott_data.products:
            raise HTTPException(status_code=503, detail="Dataset not available")
        
        result = boycott_data.search_products(product_name, limit=1)
        
        if result:
            return {
                "found": True,
                "product": result[0],
                "message": f"⚠️ {result[0]['boycott_product']} is on the boycott list"
            }
        else:
            return {
                "found": False,
                "product": None,
                "message": "✅ Product not on boycott list"
            }
    
    except Exception as e:
        logger.error(f"Error checking product: {e}")
        raise HTTPException(status_code=400, detail="Invalid product name")

# Search endpoint with advanced features
@app.get("/api/search")
async def search_products(q: str = Query(..., min_length=1, max_length=100), limit: int = Query(50, ge=1, le=100)):
    """Search products with sanitized input"""
    try:
        query = validate_query(q)
        results = boycott_data.search_products(query, limit=limit)
        
        return {
            "query": query,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

# Get all boycotts endpoint
@app.get("/api/boycotts")
async def list_boycotts(limit: int = Query(100, ge=1, le=500)):
    """List all boycotted products with pagination"""
    if not boycott_data.products:
        raise HTTPException(status_code=503, detail="Dataset not available")
    
    return boycott_data.products[:limit]

# Get categories endpoint
@app.get("/api/categories")
async def get_categories():
    """Get all product categories"""
    return {
        "categories": boycott_data.get_categories(),
        "count": len(boycott_data.get_categories()),
        "timestamp": datetime.now().isoformat()
    }

# Get by category endpoint
@app.get("/api/category/{category}")
async def get_by_category(category: str = Query(..., min_length=1, max_length=50)):
    """Get products by category"""
    try:
        category = sanitize_input(category)
        products = boycott_data.get_by_category(category)
        
        return {
            "category": category,
            "count": len(products),
            "products": products,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid category")

# Get by intensity endpoint
@app.get("/api/intensity/{intensity}")
async def get_by_intensity(intensity: str):
    """Get products by boycott intensity (High, Medium, Low)"""
    try:
        products = boycott_data.get_by_intensity(intensity)
        
        return {
            "intensity": intensity,
            "count": len(products),
            "products": products,
            "timestamp": datetime.now().isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Statistics endpoint with caching
@app.get("/api/stats")
async def get_stats():
    """Get statistics on boycotted products"""
    if not boycott_data.products:
        raise HTTPException(status_code=503, detail="Dataset not available")
    
    return boycott_data.get_stats()

# Download endpoint (CSV format)
@app.get("/api/download")
async def download_csv():
    """Download boycott list as CSV"""
    if not boycott_data.products:
        raise HTTPException(status_code=503, detail="Dataset not available")
    
    try:
        # Create CSV content
        csv_content = "id,boycott_product,brand,category,reason,tunisian_alternative,alternative_brand,intensity\n"
        
        for product in boycott_data.products:
            csv_content += f"{product.get('id', '')},{product.get('boycott_product', '')},{product.get('brand', '')},{product.get('category', '')},{product.get('reason', '')},{product.get('tunisian_alternative', '')},{product.get('alternative_brand', '')},{product.get('intensity', '')}\n"
        
        return StreamingResponse(
            iter([csv_content.encode('utf-8')]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=boycott_products.csv"}
        )
    
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail="Download failed")

# Alternatives endpoint
@app.get("/api/alternatives")
async def get_alternatives(product_name: str = Query(..., min_length=1, max_length=100)):
    """Get Tunisian alternatives for a boycotted product"""
    try:
        product_name = sanitize_input(product_name)
        results = boycott_data.search_products(product_name, limit=1)
        
        if results:
            product = results[0]
            return {
                "product": product['boycott_product'],
                "brand": product['brand'],
                "alternative": product['tunisian_alternative'],
                "alternative_brand": product['alternative_brand'],
                "category": product['category'],
                "message": f"🇹🇳 Support {product['tunisian_alternative']} instead of {product['boycott_product']}"
            }
        else:
            return {
                "found": False,
                "message": "Product not on boycott list"
            }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid product name")

# Feedback endpoint (simple logging)
@app.post("/api/feedback")
async def send_feedback(request: Request):
    """Send feedback about the application"""
    try:
        body = await request.json()
        
        # Sanitize feedback
        feedback = sanitize_input(body.get('message', ''), max_length=500)
        email = sanitize_input(body.get('email', ''), max_length=100)
        
        logger.info(f"Feedback from {email}: {feedback}")
        
        return {
            "status": "received",
            "message": "Thank you for your feedback",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail="Error processing feedback")

# Solidarity message endpoint
@app.get("/api/message")
async def get_message():
    """Get solidarity message"""
    messages = [
        "🇵🇸 Every purchase is a political choice",
        "🇵🇸 Boycott, Divestment, Sanctions - BDS",
        "🇵🇸 Support Palestinian rights",
        "🇵🇸 Choose Tunisian, Choose Palestine",
        "🇵🇸 Free Palestine from the river to the sea",
        "🇵🇸 Your wallet is your weapon - use it wisely"
    ]
    import random
    return {
        "message": random.choice(messages),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.warning(f"HTTP Exception: {exc.detail} - {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )
