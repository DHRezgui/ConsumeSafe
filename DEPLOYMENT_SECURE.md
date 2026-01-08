# ConsumeSafe Secure Deployment Guide v2.0

## 🎯 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Virtual Environment
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/ConsumeSafe.git
cd ConsumeSafe

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start API server
python -m uvicorn ConsumeSafe.app.main:app --host 127.0.0.1 --port 8000

# Start frontend (in new terminal)
cd ConsumeSafe/app
python -m http.server 8080

# Access application
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/api/docs
```

---

## 🐳 Docker Deployment (Recommended)

### Build Image
```bash
# Build Docker image
docker build -t consumesafe:latest .

# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image consumesafe:latest
```

### Run Container
```bash
# Run single container
docker run -d \
  --name consumesafe \
  -p 8000:8000 \
  -e LOG_LEVEL=info \
  -e RATE_LIMIT=100 \
  --restart unless-stopped \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  consumesafe:latest

# Check container status
docker logs consumesafe
docker ps
```

### Docker Compose (Development)
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run health check
docker-compose exec api curl http://localhost:8000/api/health
```

---

## ☸️ Kubernetes Deployment (Production)

### Prerequisites
- Kubernetes 1.20+
- kubectl configured
- Helm (optional)

### Deployment Steps

#### 1. Create Namespace
```bash
kubectl create namespace consumesafe
kubectl label namespace consumesafe name=consumesafe
```

#### 2. Apply ConfigMaps
```bash
kubectl apply -f k8s/configmaps.yaml -n consumesafe
```

#### 3. Apply Security Policies
```bash
# RBAC
kubectl apply -f k8s/security.yaml -n consumesafe

# Network Policies
kubectl apply -f k8s/network-policy.yaml -n consumesafe

# Pod Security Policy
kubectl apply -f k8s/pod-security-policy.yaml -n consumesafe
```

#### 4. Deploy Application
```bash
kubectl apply -f k8s/deployment.yaml -n consumesafe
```

#### 5. Apply Ingress
```bash
# If using Ingress Controller
kubectl apply -f k8s/ingress.yaml -n consumesafe

# For development (Port Forward)
kubectl port-forward -n consumesafe svc/consumesafe-api 8000:8000
```

#### 6. Verify Deployment
```bash
# Check pods
kubectl get pods -n consumesafe

# Check services
kubectl get svc -n consumesafe

# Check ingress
kubectl get ingress -n consumesafe

# View logs
kubectl logs -n consumesafe deployment/consumesafe-api -f

# Run health check
kubectl exec -it -n consumesafe \
  $(kubectl get pod -n consumesafe -o jsonpath='{.items[0].metadata.name}') \
  -- curl http://localhost:8000/api/health
```

### Kubernetes Security Hardening

#### Resource Limits
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

#### Network Policy
```yaml
# Restrict ingress to API port only
# Restrict egress to DNS and optional external APIs
```

#### Pod Disruption Budget
```yaml
minAvailable: 1  # Keep at least 1 pod running
```

---

## 🔒 SSL/TLS Configuration

### NGINX with Let's Encrypt
```nginx
server {
    listen 443 ssl http2;
    server_name consumesafe.example.com;
    
    ssl_certificate /etc/letsencrypt/live/consumesafe.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/consumesafe.example.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://consumesafe-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name consumesafe.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Kubernetes TLS with cert-manager
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f k8s/cert-issuer.yaml

# Update Ingress with TLS
kubectl annotate ingress consumesafe-ingress -n consumesafe \
  cert-manager.io/cluster-issuer=letsencrypt-prod --overwrite
```

---

## 📊 Monitoring & Logging

### Prometheus Metrics
```bash
# Add Prometheus endpoint
# /metrics endpoint for scraping
```

### ELK Stack (Elasticsearch, Logstash, Kibana)
```bash
# Install ELK
docker-compose -f docker-compose.elk.yml up

# Configure log shipping
python -c "
from pythonjsonlogger import jsonlogger
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
"
```

### Kubernetes Logging
```bash
# Check logs
kubectl logs -n consumesafe deployment/consumesafe-api -f

# View events
kubectl describe pod -n consumesafe

# Export logs
kubectl logs -n consumesafe --all-containers=true deployment/consumesafe-api > app.log
```

---

## 🧪 Security Testing Checklist

### Pre-Deployment
- [ ] Run security tests: `pytest tests/test_security.py -v`
- [ ] Check dependencies: `safety check`
- [ ] SAST scan: `bandit -r ConsumeSafe/app`
- [ ] Code review completed
- [ ] All tests passing

### Post-Deployment
- [ ] Health check passing
- [ ] Logging functioning
- [ ] Metrics available
- [ ] Alerts configured
- [ ] Backup/recovery tested

### Monthly
- [ ] Penetration testing
- [ ] Dependency updates
- [ ] Security audit
- [ ] Incident response drill

---

## 🚨 Incident Response

### Suspicious Activity
```bash
# 1. Check logs for anomalies
kubectl logs -n consumesafe deployment/consumesafe-api | grep ERROR

# 2. Check rate limiting
grep "429" /var/log/consumesafe.log

# 3. Check security violations
grep "XSS\|injection\|unauthorized" /var/log/consumesafe.log

# 4. Isolate if needed
kubectl set env deployment/consumesafe-api -n consumesafe \
  MAINTENANCE_MODE=true
```

### Rollback Procedure
```bash
# View deployment history
kubectl rollout history deployment/consumesafe-api -n consumesafe

# Rollback to previous version
kubectl rollout undo deployment/consumesafe-api -n consumesafe

# Verify rollback
kubectl get pods -n consumesafe
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Code review approved
- [ ] Deployment plan reviewed
- [ ] Backup created

### Deployment
- [ ] Environment variables set
- [ ] SSL/TLS certificates installed
- [ ] Health checks configured
- [ ] Monitoring enabled
- [ ] Logging enabled

### Post-Deployment
- [ ] Application accessible
- [ ] API responding
- [ ] Health checks passing
- [ ] Logs being collected
- [ ] Metrics available
- [ ] Alerts configured

### Validation
- [ ] Search functionality works
- [ ] Download functionality works
- [ ] Rate limiting working
- [ ] Security headers present
- [ ] HTTPS redirecting (if applicable)

---

## 🔧 Troubleshooting

### API Won't Start
```bash
# Check logs
docker logs consumesafe

# Verify port is available
lsof -i :8000

# Check configuration
echo $CONSUMESAFE_CONFIG

# Try with verbose logging
python -m uvicorn ConsumeSafe.app.main:app \
  --host 0.0.0.0 --port 8000 --log-level debug
```

### Health Check Failing
```bash
# Test endpoint directly
curl http://127.0.0.1:8000/api/health

# Check if API is responding
curl -v http://127.0.0.1:8000/api/health

# View detailed error
curl http://127.0.0.1:8000/api/health 2>&1 | head -20
```

### Rate Limiting Issues
```bash
# Check rate limit configuration
grep -i "rate_limit" ConsumeSafe/app/main.py

# Test rate limiting
for i in {1..101}; do curl http://127.0.0.1:8000/api/health; done

# Monitor requests
tail -f /var/log/consumesafe.log | grep "429"
```

### Database Issues
```bash
# Verify CSV file exists
ls -lah ConsumeSafe/data/boycott_products.csv

# Check file permissions
stat ConsumeSafe/data/boycott_products.csv

# Validate CSV format
head -1 ConsumeSafe/data/boycott_products.csv
wc -l ConsumeSafe/data/boycott_products.csv
```

---

## 📞 Support

For issues or questions:
1. Check logs: `kubectl logs -n consumesafe deployment/consumesafe-api`
2. Check health: `curl http://api:8000/api/health`
3. Review SECURITY.md for security issues
4. Open GitHub issue with details

---

**Last Updated**: January 6, 2026  
**Version**: 2.0.0  
**Status**: Production Ready ✅
