from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import csv
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json
import time
from pydantic import BaseModel

# Import AI Service
from app.ai_service import create_ai_service

# Import Monitoring
from app.monitoring import initialize_monitoring, RequestLogger, PrometheusMetrics

# Initialize monitoring (logging and metrics)
logger = initialize_monitoring()
PrometheusMetrics.initialize()

app = FastAPI(
    title="ConsumeSafe",
    description="Check if products are boycotted and find Tunisian alternatives",
    version="1.0.0"
)

# Add middleware for request tracking
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Middleware to track all requests."""
    import uuid
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log request
    RequestLogger.log_request(
        logger,
        request.method,
        request.url.path,
        request_id=request_id
    )
    
    try:
        response = await call_next(request)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        RequestLogger.log_error(
            logger,
            "RequestError",
            str(e),
            request_id=request_id
        )
        raise
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Log response
    RequestLogger.log_response(
        logger,
        response.status_code,
        duration_ms,
        request_id=request_id
    )
    
    # Update Prometheus metrics
    if PrometheusMetrics.REQUEST_COUNT:
        PrometheusMetrics.REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        PrometheusMetrics.REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration_ms / 1000)
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration_ms)
    
    return response

# Trusted hosts middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'boycott_products.csv')
HTML_PATH = os.path.join(os.path.dirname(__file__), 'index.html')

class BoycottData:
    def __init__(self):
        self.products = []
        self.load_data()
    
    def load_data(self):
        """Load boycott products dataset from CSV"""
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.products = list(reader)
            logger.info(f"Loaded {len(self.products)} boycott products")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.products = []
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search products by name or brand (case-insensitive)"""
        query_lower = query.lower()
        results = []
        for product in self.products:
            if (query_lower in product.get('boycott_product', '').lower() or
                query_lower in product.get('brand', '').lower()):
                results.append(product)
        return results
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category"""
        category_lower = category.lower()
        return [p for p in self.products 
                if p.get('category', '').lower() == category_lower]
    
    def get_by_intensity(self, intensity: str) -> List[Dict[str, Any]]:
        """Get products by intensity"""
        intensity_lower = intensity.lower()
        return [p for p in self.products 
                if p.get('intensity', '').lower() == intensity_lower]
    
    def get_categories(self) -> List[str]:
        """Get unique categories"""
        categories = set()
        for product in self.products:
            cat = product.get('category', '').strip()
            if cat:
                categories.add(cat)
        return sorted(list(categories))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        intensity_count = {}
        category_count = {}
        
        for product in self.products:
            intensity = product.get('intensity', 'Unknown')
            category = product.get('category', 'Unknown')
            
            intensity_count[intensity] = intensity_count.get(intensity, 0) + 1
            category_count[category] = category_count.get(category, 0) + 1
        
        return {
            'total_products': len(self.products),
            'categories': len(self.get_categories()),
            'by_intensity': intensity_count,
            'by_category': category_count
        }

# Initialize data
boycott_data = BoycottData()
ai_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global boycott_data, ai_service
    boycott_data = BoycottData()
    ai_service = create_ai_service(boycott_data.products)
    logger.info("ConsumeSafe API started successfully")
    logger.info("AI Service initialized")

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse(HTML_PATH, media_type="text/html")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from prometheus_client import generate_latest
        return generate_latest()
    except ImportError:
        return JSONResponse(
            {"error": "Prometheus not available"},
            status_code=503
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "products_loaded": len(boycott_data.products)
    }

@app.get("/api/check")
async def check_product(product_name: str = Query(..., min_length=1)):
    """Check if a product is on the boycott list"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    matching = boycott_data.search_products(product_name)
    
    if not matching:
        return {
            "status": "safe",
            "product": product_name,
            "message": "This product is NOT on our boycott list",
            "recommendation": "You can purchase this product safely"
        }
    
    results = []
    for row in matching:
        results.append({
            "id": row.get('id'),
            "product": row.get('boycott_product'),
            "brand": row.get('brand'),
            "category": row.get('category'),
            "reason": row.get('reason'),
            "intensity": row.get('intensity'),
            "tunisian_alternative": row.get('tunisian_alternative'),
            "alternative_brand": row.get('alternative_brand')
        })
    
    return {
        "status": "boycotted",
        "product": product_name,
        "found_items": results,
        "message": f"⚠️ Found {len(results)} product(s) to avoid",
        "solidarity": "Stand with Palestine 🇵🇸"
    }

@app.get("/api/alternatives")
async def get_alternatives(product_name: str = Query(..., min_length=1)):
    """Get Tunisian alternatives for boycotted products"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    matching = boycott_data.search_products(product_name)
    
    if not matching:
        return {
            "status": "not_found",
            "message": f"Product '{product_name}' not on boycott list"
        }
    
    alternatives = []
    for row in matching:
        alternatives.append({
            "boycott_product": row.get('boycott_product'),
            "brand": row.get('brand'),
            "category": row.get('category'),
            "reason": row.get('reason'),
            "tunisian_alternative": row.get('tunisian_alternative'),
            "alternative_brand": row.get('alternative_brand'),
            "impact": f"By choosing {row.get('tunisian_alternative')}, you support local Tunisian business! 🇹🇳"
        })
    
    return {
        "status": "success",
        "alternatives": alternatives,
        "message": "Choose Tunisian! Support Palestine! 🇵🇸",
        "total_alternatives": len(alternatives)
    }

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    intensity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """Get list of all boycotted products - Compatible with frontend"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    results = boycott_data.products.copy()
    
    if category:
        results = boycott_data.get_by_category(category)
    
    if intensity:
        results = [p for p in results if p.get('intensity', '').lower() == intensity.lower()]
    
    results = results[:limit]
    
    products = []
    for row in results:
        products.append({
            "id": row.get('id'),
            "Product Name": row.get('boycott_product'),
            "Brand": row.get('brand'),
            "Category": row.get('category'),
            "Reason": row.get('reason'),
            "Intensity": row.get('intensity'),
            "Tunisian Alternative": row.get('tunisian_alternative'),
            "Alternative Brand": row.get('alternative_brand')
        })
    
    return products

@app.get("/api/boycotts")
async def list_all_boycotts(
    category: Optional[str] = None,
    intensity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """Get list of all boycotted products"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    results = boycott_data.products.copy()
    
    if category:
        results = boycott_data.get_by_category(category)
    
    if intensity:
        results = [p for p in results if p.get('intensity', '').lower() == intensity.lower()]
    
    results = results[:limit]
    
    products = []
    for row in results:
        products.append({
            "id": row.get('id'),
            "product": row.get('boycott_product'),
            "brand": row.get('brand'),
            "category": row.get('category'),
            "reason": row.get('reason'),
            "intensity": row.get('intensity'),
            "tunisian_alternative": row.get('tunisian_alternative'),
            "alternative_brand": row.get('alternative_brand')
        })
    
    return {
        "status": "success",
        "total": len(products),
        "products": products,
        "message": "Every purchase is a vote. Choose Palestine! 🇵🇸"
    }

@app.get("/api/categories")
async def get_categories():
    """Get all product categories"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    categories = boycott_data.get_categories()
    return {
        "categories": categories,
        "count": len(categories)
    }

@app.get("/api/stats")
async def get_statistics():
    """Get statistics about boycotted products"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    stats = boycott_data.get_stats()
    stats["message"] = "Knowledge is power. Share this information! 🇵🇸"
    return stats

@app.get("/api/download/boycott_list.csv")
async def download_boycott_list():
    """Download complete boycott list as CSV"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    try:
        return FileResponse(
            DATA_PATH,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=boycott_products.csv"}
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail="Error generating download")

@app.get("/api/search")
async def search_product(q: str = Query(..., min_length=1)):
    """Search products by name or brand"""
    if not boycott_data.products:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    q_lower = q.lower()
    results = []
    for product in boycott_data.products:
        if (q_lower in product.get('boycott_product', '').lower() or
            q_lower in product.get('brand', '').lower() or
            q_lower in product.get('tunisian_alternative', '').lower()):
            results.append(product)
    
    if not results:
        return {"status": "no_results", "message": f"No results for '{q}'"}
    
    products = []
    for row in results:
        products.append({
            "id": row.get('id'),
            "product": row.get('boycott_product'),
            "brand": row.get('brand'),
            "category": row.get('category'),
            "tunisian_alternative": row.get('tunisian_alternative'),
            "alternative_brand": row.get('alternative_brand')
        })
    
    return {
        "status": "success",
        "query": q,
        "results_count": len(products),
        "results": products
    }

@app.post("/api/feedback")
async def submit_feedback(feedback: dict):
    """Submit feedback about products"""
    try:
        timestamp = datetime.now().isoformat()
        feedback['timestamp'] = timestamp
        
        logger.info(f"Feedback received: {feedback}")
        
        return {
            "status": "success",
            "message": "Thank you for your feedback! Together we stand with Palestine 🇵🇸",
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail="Error processing feedback")

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
    return {"message": random.choice(messages)}

# ============ AI ENDPOINTS ============

class ChatMessage(BaseModel):
    message: str

class FeedbackAnalysis(BaseModel):
    feedback: str

@app.post("/api/ai/chat")
async def chat_with_ai(chat_msg: ChatMessage):
    """Chat with AI about boycott products"""
    if not ai_service:
        raise HTTPException(status_code=500, detail="AI Service not initialized")
    
    try:
        response = ai_service.chat(chat_msg.message)
        return {
            "status": "success",
            "user_message": chat_msg.message,
            "ai_response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

@app.post("/api/ai/recommend")
async def get_recommendations(history: List[str] = Query(...)):
    """Get personalized product recommendations"""
    if not ai_service:
        raise HTTPException(status_code=500, detail="AI Service not initialized")
    
    try:
        recommendations = ai_service.get_recommendations(history, limit=5)
        return {
            "status": "success",
            "recommendations": recommendations,
            "total": len(recommendations),
            "message": "Personalized recommendations based on your search history"
        }
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")

@app.post("/api/ai/analyze-sentiment")
async def analyze_feedback_sentiment(feedback_analysis: FeedbackAnalysis):
    """Analyze sentiment of user feedback"""
    if not ai_service:
        raise HTTPException(status_code=500, detail="AI Service not initialized")
    
    try:
        analysis = ai_service.analyze_sentiment(feedback_analysis.feedback)
        return {
            "status": "success",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing sentiment")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
