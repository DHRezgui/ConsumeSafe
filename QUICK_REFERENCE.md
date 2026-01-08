# ConsumeSafe - Quick Reference Guide

## 🚀 Start Here

### 30-Second Setup
```bash
cd ConsumeSafe
cp .env.example .env
docker-compose up -d
# Wait 30 seconds...
# Open: http://localhost:3000
```

### 5-Minute Validation
```bash
./validate-project.sh        # Check everything
./health-check.sh             # Verify health
pytest tests/ -v              # Run tests
docker-compose logs -f        # View logs
```

---

## 📱 Application URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | User interface |
| **API** | http://localhost:8000 | Backend API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Metrics** | http://localhost:8000/metrics | Prometheus metrics |
| **Health** | http://localhost:8000/api/health | Health check |

---

## 🔨 Common Commands

### Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api              # API logs
docker-compose logs -f frontend         # Frontend logs
docker-compose logs                     # All logs

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Shell into container
docker-compose exec api bash
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_backend.py -v

# Run specific test
pytest tests/test_backend.py::TestProductEndpoints::test_search -v

# Coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# Performance tests
pytest tests/ -v --durations=10
```

### Production (Kubernetes)
```bash
# Deploy
./deploy.sh

# Check status
kubectl get pods -n consumesafe
kubectl get svc -n consumesafe

# View logs
kubectl logs -n consumesafe deployment/consumesafe-api

# Port forward
kubectl port-forward -n consumesafe svc/consumesafe-api 8000:8000

# Scale replicas
kubectl scale deployment consumesafe-api --replicas=5 -n consumesafe

# Rollback
./deploy.sh rollback
```

---

## 📊 API Quick Reference

### Search Products
```bash
curl "http://localhost:8000/api/search?query=nestle"
```

### Check Product
```bash
curl "http://localhost:8000/api/check?product=Sprite"
```

### Get Categories
```bash
curl "http://localhost:8000/api/categories"
```

### Get Statistics
```bash
curl "http://localhost:8000/api/stats"
```

### AI Chat
```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Why boycott Nestle?"}'
```

### AI Recommendations
```bash
curl -X POST "http://localhost:8000/api/ai/recommend" \
  -H "Content-Type: application/json" \
  -d '{"user_history":["Nestle","Coca-Cola"]}'
```

### AI Sentiment
```bash
curl -X POST "http://localhost:8000/api/ai/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text":"This app is amazing!"}'
```

---

## 🐛 Troubleshooting

### API Not Responding
```bash
# Check if service is running
docker ps

# Restart service
docker-compose restart api

# Check logs
docker-compose logs api

# Health check
curl http://localhost:8000/api/health
```

### High Memory Usage
```bash
# Check memory
docker stats

# Restart to clear
docker-compose restart api

# Check data size
wc -l data/boycott_products.csv
```

### Tests Failing
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run with more verbose output
pytest tests/ -vv -s

# Check specific test
pytest tests/test_backend.py::TestHealth -vv
```

### Docker Issues
```bash
# Clear everything
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## 📈 Monitoring

### View Metrics
```bash
# Prometheus format
curl http://localhost:8000/metrics

# Specific metric
curl http://localhost:8000/metrics | grep consumesafe_requests_total

# Custom query
curl 'http://localhost:9090/api/v1/query?query=rate(consumesafe_requests_total[5m])'
```

### Check Health
```bash
# API health
curl http://localhost:8000/api/health | jq

# All services
./health-check.sh
```

### View Logs
```bash
# Recent logs
docker-compose logs --tail=50 api

# Follow logs
docker-compose logs -f api

# JSON logs (if configured)
docker-compose logs api | jq
```

---

## 🔐 Security Quick Checks

### Verify CORS
```bash
curl -i -X OPTIONS http://localhost:8000/api/products \
  -H "Origin: http://example.com"
```

### Test Rate Limiting
```bash
# Should allow 100 requests per minute
for i in {1..102}; do
  curl -s http://localhost:8000/api/products > /dev/null
  echo "Request $i"
done
```

### Check SSL (Production)
```bash
openssl s_client -connect consumesafe.com:443
```

---

## 📝 Configuration Quick Guide

### Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Key variables:
# ENV=production              # or development
# DEBUG=False                 # production setting
# SECRET_KEY=<random>        # generate with: openssl rand -hex 32
# API_PORT=8000              # default port
# CORS_ORIGINS=yourdomain.com
# AI_ENABLED=true            # enable AI features
```

### Docker Compose Override
```bash
# Create docker-compose.override.yml for local changes
# Example:
version: '3'
services:
  api:
    environment:
      DEBUG: "true"
    ports:
      - "8001:8000"  # Different port
```

---

## 🚀 Deployment Quick Start

### To Production
```bash
# 1. Ensure all tests pass
pytest tests/ -v

# 2. Validate project
./validate-project.sh

# 3. Configure environment
cp .env.example .env
nano .env

# 4. Build image
docker build -t consumesafe:latest .

# 5. Deploy to Kubernetes
./deploy.sh

# 6. Verify deployment
kubectl get pods -n consumesafe
./health-check.sh
```

### Rollback (if issues)
```bash
./deploy.sh rollback
kubectl rollout status deployment/consumesafe-api -n consumesafe
```

---

## 📚 Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **README.md** | Project overview | 5 min |
| **QUICK_REFERENCE.md** | This file | 5 min |
| **PRODUCTION_GUIDE.md** | Comprehensive guide | 20 min |
| **API documentation** | API endpoints | 15 min |
| **SECURITY.md** | Security details | 10 min |
| **DEPLOYMENT.md** | Deployment process | 15 min |

---

## 🎯 Quick Debugging

### 1. Is the app running?
```bash
curl http://localhost:8000/api/health
```

### 2. Are tests passing?
```bash
pytest tests/ -v
```

### 3. Check data loaded?
```bash
curl http://localhost:8000/api/stats
```

### 4. AI service working?
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

### 5. Check logs
```bash
docker-compose logs --tail=20 api
```

---

## 💡 Performance Tips

### For Development
- Use `DEBUG=true` in `.env` for auto-reload
- Run tests with `-x` flag to stop at first failure
- Use `docker-compose logs -f` instead of checking logs manually

### For Production
- Set `DEBUG=false`
- Use multiple replicas: `kubectl scale deployment consumesafe-api --replicas=3`
- Enable caching if using Redis
- Monitor metrics dashboard regularly

### API Performance
- Search should be <500ms
- Chat should be <500ms
- Health check should be <100ms
- If slow, check: data size, CPU, memory, network

---

## 🔄 Upgrade Procedure

```bash
# 1. Pull latest changes
git pull origin main

# 2. Install new dependencies
pip install -r requirements.txt

# 3. Run tests
pytest tests/ -v

# 4. Rebuild Docker image
docker-compose build --no-cache

# 5. Deploy
./deploy.sh

# 6. Verify
./health-check.sh

# 7. Monitor for errors
docker-compose logs -f api
```

---

## 📞 Support

### Where to Find Help
1. **README.md** - General questions
2. **PRODUCTION_GUIDE.md** - Deployment issues
3. **Logs** - `docker-compose logs api`
4. **Tests** - `pytest tests/ -vv`
5. **API Docs** - http://localhost:8000/docs

### Common Issues
- App not starting? → Check logs, check port availability
- Tests failing? → Check Python version, dependencies
- High CPU? → Check query performance, database
- High memory? → Check data size, restart service

---

## ✨ Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias cs-start="docker-compose up -d"
alias cs-stop="docker-compose down"
alias cs-logs="docker-compose logs -f api"
alias cs-test="pytest tests/ -v"
alias cs-health="./health-check.sh"
alias cs-validate="./validate-project.sh"
alias cs-shell="docker-compose exec api bash"
alias cs-deploy="./deploy.sh"
```

---

**Updated**: 2024-01-15  
**Status**: ✅ Production Ready
