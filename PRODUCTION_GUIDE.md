# ConsumeSafe - Complete Production Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Deployment](#deployment)
4. [API Documentation](#api-documentation)
5. [Monitoring & Logging](#monitoring--logging)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd ConsumeSafe

# Setup environment
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Application will be available at:
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn app.main:app --reload --port 8000

# Serve frontend (separate terminal)
cd app && python -m http.server 3000

# Access at http://localhost:3000
```

---

## 🏗️ Architecture

### Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                   Frontend                           │
│  HTML5 + Tailwind CSS + Vanilla JavaScript          │
│  Nginx Reverse Proxy (Production)                   │
└────────────────┬────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────┐
│                  API Gateway                         │
│  FastAPI + Uvicorn ASGI Server                      │
│  Rate Limiting | CORS | Auth Ready                  │
└────────────────┬────────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌───▼────┐ ┌───▼────┐
│  Data   │ │   AI   │ │ Logs & │
│  Layer  │ │Service │ │Metrics │
│(CSV DB) │ │        │ │        │
└─────────┘ └────────┘ └────────┘
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Frontend** | User Interface | HTML5, Tailwind CSS, JavaScript |
| **API Server** | Business Logic | FastAPI, Python 3.11 |
| **AI Service** | Chat, Recommendations, Sentiment | Custom ML module |
| **Database** | Boycott Data | CSV (upgradeable to SQL) |
| **Container** | Deployment | Docker & Kubernetes |
| **Monitoring** | Observability | Prometheus + Grafana |
| **Reverse Proxy** | Load Balancing | Nginx |

---

## 🚢 Deployment

### Docker Compose (Development/Staging)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild images
docker-compose up -d --build
```

### Kubernetes (Production)

```bash
# Deploy to cluster
./deploy.sh

# Check deployment status
kubectl get pods -n consumesafe
kubectl get svc -n consumesafe

# View logs
kubectl logs -n consumesafe deployment/consumesafe-api

# Rollback if needed
./deploy.sh rollback

# Port forward for local testing
kubectl port-forward -n consumesafe svc/consumesafe-api 8000:8000
```

### Environment Configuration

Create `.env` from template:

```bash
cp .env.example .env
```

Key variables:

```env
# Application
ENV=production
DEBUG=False
SECRET_KEY=<generate-random-secure-key>

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
FRONTEND_URL=https://yourdomain.com

# Security
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_REQUESTS=100

# AI
AI_ENABLED=true

# Monitoring
PROMETHEUS_METRICS_ENABLED=true
```

---

## 📡 API Documentation

### Base URL
```
Development: http://localhost:8000
Production: https://api.consumesafe.com
```

### Interactive Docs
- Swagger UI: `GET /docs`
- ReDoc: `GET/redoc`

### Core Endpoints

#### 1. **Product Search**
```http
GET /api/search?query=nestle
```

**Response:**
```json
{
  "results": [
    {
      "name": "Nestle Coffee",
      "category": "Beverages",
      "intensity": "high",
      "reason": "..."
    }
  ]
}
```

#### 2. **Check Product Status**
```http
GET /api/check?product=Sprite
```

**Response:**
```json
{
  "boycotted": true,
  "category": "Beverages",
  "intensity": "high"
}
```

#### 3. **Get All Products**
```http
GET /api/products?category=Beverages&intensity=high
```

#### 4. **Find Alternatives**
```http
GET /api/alternatives?product=Coca-Cola
```

**Response:**
```json
{
  "alternatives": [
    {
      "name": "Local Tunisian Beverage",
      "category": "Beverages",
      "recommended": true
    }
  ]
}
```

#### 5. **Statistics**
```http
GET /api/stats
```

**Response:**
```json
{
  "total_products": 150,
  "total_categories": 26,
  "products_by_intensity": {...},
  "top_boycotts": [...]
}
```

#### 6. **AI Chatbot**
```http
POST /api/ai/chat
Content-Type: application/json

{
  "message": "Why should I boycott Nestle?"
}
```

**Response:**
```json
{
  "response": "Nestle boycott is important because...",
  "intent": "why_boycott"
}
```

#### 7. **AI Recommendations**
```http
POST /api/ai/recommend
Content-Type: application/json

{
  "user_history": ["Nestle", "Coca-Cola"]
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "name": "Alternative Product",
      "score": 0.87
    }
  ]
}
```

#### 8. **AI Sentiment Analysis**
```http
POST /api/ai/analyze-sentiment
Content-Type: application/json

{
  "text": "This app is amazing!"
}
```

**Response:**
```json
{
  "sentiment": "positive",
  "category": "UI/UX",
  "suggestion": "Continue improving UI/UX features"
}
```

### Error Responses

```json
{
  "detail": "Product not found",
  "status_code": 404
}
```

---

## 📊 Monitoring & Logging

### Health Check

```bash
./health-check.sh

# Output:
# [✓] /api/health - HTTP 200
# [✓] /api/products - HTTP 200
# [✓] Frontend accessible
# All checks passed!
```

### Prometheus Metrics

Metrics available at `GET /metrics`:

```
# API Metrics
consumesafe_requests_total{method="GET",endpoint="/api/products",status="200"} 1234
consumesafe_request_duration_seconds_bucket{method="GET",endpoint="/api/products",le="0.5"} 950

# AI Metrics
consumesafe_ai_chat_total{intent="why_boycott"} 234
consumesafe_ai_recommendation_total 567

# Error Metrics
consumesafe_errors_total{type="validation_error",endpoint="/api/check"} 12
```

### Logging

Logs are available in `logs/consumesafe.log` in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "message": "Chat: intent=why_boycott, duration=45ms",
  "logger": "app.ai_service",
  "request_id": "a1b2c3d4"
}
```

### Grafana Dashboard

1. Add Prometheus data source: `http://prometheus:9090`
2. Import dashboard from `k8s/grafana-dashboard.json`
3. Visualizations include:
   - Requests per second
   - Error rate
   - Response time (p95)
   - AI service metrics
   - Search performance

### Alert Rules

Prometheus alert rules in `k8s/alert-rules.yaml`:

- **HighErrorRate**: Error rate > 5% for 5 minutes
- **SlowResponseTime**: p95 latency > 1s
- **HighMemoryUsage**: > 500MB
- **LowDiskSpace**: < 1GB available

---

## 🧪 Testing

### Run All Tests

```bash
# Unit tests
pytest tests/test_backend.py -v

# AI service tests
pytest tests/test_ai_service.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test
pytest tests/test_backend.py::TestProductEndpoints::test_search_products -v
```

### Test Coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing

# Target: >80% coverage
# Key areas: AI service, API endpoints, data loading
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/test_integration.py -v

# Cleanup
docker-compose down
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **API returns 502 Bad Gateway**
```bash
# Check if API service is running
docker ps | grep consumesafe

# Check logs
docker logs consumesafe-api

# Restart service
docker-compose restart api
```

#### 2. **High Memory Usage**
```bash
# Check process memory
docker stats consumesafe-api

# Solutions:
# - Increase container limits in docker-compose.yml
# - Optimize data loading
# - Check for memory leaks in AI service
```

#### 3. **Search Endpoint Slow**
```bash
# Monitor search performance
curl "http://localhost:8000/api/search?query=test" -w "\nTime: %{time_total}s\n"

# Check Prometheus metrics
# consumesafe_search_duration_seconds

# Solutions:
# - Index CSV data
# - Use database instead of CSV
# - Implement caching
```

#### 4. **AI Service Crashes**
```bash
# Check AI service logs
docker logs consumesafe-api | grep "ai_service"

# Verify data loading
curl http://localhost:8000/api/products

# Restart API
docker-compose restart api
```

### Performance Optimization

```bash
# 1. Enable caching
# - Redis for product cache
# - Browser caching headers
# - AI response caching

# 2. Database migration
# - Replace CSV with PostgreSQL
# - Index frequently searched columns
# - Connection pooling

# 3. Frontend optimization
# - Enable compression
# - Minify CSS/JS
# - Lazy load images

# 4. API optimization
# - Add response caching
# - Implement pagination
# - Use database indexes
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# k8s/deployment.yaml
replicas: 5  # Scale to 5 instances

# Load balancing automatically handled by Kubernetes
# Traffic distributed across pods
```

### Vertical Scaling

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### Database Scaling

```bash
# Add read replicas
# Implement master-slave setup
# Use connection pooling

# Example: Move to PostgreSQL
# - Better concurrent query handling
# - Full-text search support
# - Replication capabilities
```

---

## 🔒 Security

### Authentication (Future)

```python
# Add JWT authentication
@app.post("/api/auth/login")
async def login(credentials: Credentials):
    # Generate JWT token
    return {"token": token}

@app.get("/api/protected")
async def protected(token: str = Depends(verify_token)):
    # Protected endpoint
```

### Rate Limiting

Current: 100 requests/minute per IP

```env
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Data Encryption

```python
# Enable HTTPS
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/cert.pem
SSL_KEY_PATH=/etc/ssl/key.pem
```

---

## 📝 Contributing

### Code Style

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/

# Type checking (future)
mypy app/
```

### Making Changes

1. Create feature branch
2. Make changes
3. Add tests
4. Run test suite
5. Create pull request

### Commit Messages

```
feat: Add new AI feature
fix: Resolve search bug
docs: Update API documentation
test: Add unit tests for products
chore: Update dependencies
```

---

## 📞 Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs: `docker logs consumesafe-api`
3. Open GitHub issue with details
4. Contact maintainers

---

## 📄 License

See LICENSE file for details.

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready ✅
