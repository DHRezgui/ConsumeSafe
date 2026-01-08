# ConsumeSafe - Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [CI/CD Setup](#cicd-setup)
5. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation & Running

```bash
# Clone the repository
cd ConsumeSafe

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python quickstart.py
```

The application will automatically:
- Install all dependencies
- Start the API server on `http://localhost:8000`
- Start the frontend on `http://localhost:8080`
- Open your browser automatically

### Manual Start (if quickstart doesn't work)

**Terminal 1 - Start API:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd app
python -m http.server 8080
```

Then visit:
- Frontend: http://localhost:8080
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Docker Build & Run

```bash
# Build the image
docker build -t consumesafe-api:latest .

# Run the container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  consumesafe-api:latest

# For Windows (PowerShell):
docker run -p 8000:8000 `
  -v "$(Get-Location)/data:/app/data" `
  consumesafe-api:latest
```

### Docker Compose Troubleshooting

```bash
# View all running containers
docker-compose ps

# View logs for specific service
docker-compose logs api
docker-compose logs frontend

# Rebuild images
docker-compose build --no-cache

# Clean up (WARNING: removes all containers and volumes)
docker-compose down -v
```

## Kubernetes Deployment

### Prerequisites
- kubectl
- Kubernetes cluster (minikube, kind, EKS, GKE, AKS, etc.)
- Docker (for building images)

### Quick Deployment

```bash
# Using the deployment script (Linux/Mac)
chmod +x deploy.sh
./deploy.sh

# Or on Windows
deploy.bat
```

### Manual Kubernetes Deployment

```bash
# Build Docker image
docker build -t consumesafe-api:latest .

# Load image into local cluster (if using minikube/kind)
minikube image load consumesafe-api:latest
# or
kind load docker-image consumesafe-api:latest

# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/security.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/configmaps.yaml

# Check deployment status
kubectl get pods -n consumesafe
kubectl get svc -n consumesafe

# Wait for deployment
kubectl rollout status deployment/consumesafe-api -n consumesafe
```

### Access Application Locally

```bash
# Terminal 1 - Frontend port forwarding
kubectl port-forward svc/consumesafe-frontend 3000:80 -n consumesafe

# Terminal 2 - API port forwarding
kubectl port-forward svc/consumesafe-api 8000:8000 -n consumesafe
```

Then visit:
- Frontend: http://localhost:3000
- API: http://localhost:8000

### Check Cluster Resources

```bash
# View all resources in consumesafe namespace
kubectl get all -n consumesafe

# View detailed pod information
kubectl describe pod <pod-name> -n consumesafe

# View logs
kubectl logs <pod-name> -n consumesafe

# View events
kubectl get events -n consumesafe
```

### Scale Deployment

```bash
# Scale to 3 replicas
kubectl scale deployment consumesafe-api --replicas=3 -n consumesafe

# View scaling status
kubectl get pods -n consumesafe
```

### Delete Deployment

```bash
# Delete all resources in namespace
kubectl delete namespace consumesafe

# Or delete specific resources
kubectl delete -f k8s/
```

## CI/CD Setup

### GitHub Actions

The project includes a complete CI/CD pipeline in `.github/workflows/ci-cd.yml`.

**Features:**
- Run tests on Python 3.10 and 3.11
- Code quality checks (flake8, black, isort)
- Build Docker image
- Security scanning (Trivy)
- Automatic deployment to Kubernetes (on main branch)

### Setup

1. **Create GitHub Repository**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ConsumeSafe.git
git branch -M main
git push -u origin main
```

2. **Configure Secrets** (in GitHub Settings → Secrets)
```
KUBE_CONFIG: <base64 encoded kubeconfig>
```

3. **Enable Actions**
- Go to Actions tab
- Click "I understand my workflows"

4. **Push to trigger pipeline**
```bash
git push origin main
```

### Local CI/CD Testing

```bash
# Run linting
flake8 app/
black app/
isort app/

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t consumesafe-api:latest .
```

## Troubleshooting

### API Issues

**API won't start:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Check requirements installation
pip list | grep fastapi

# Try reinstalling dependencies
pip install --upgrade -r requirements.txt

# Run with verbose output
python -m uvicorn app.main:app --log-level debug
```

**Connection refused on localhost:8000:**
- API might still be starting, wait a few seconds
- Check if port 8000 is already in use: `netstat -ano | findstr :8000` (Windows)
- Try a different port: `python -m uvicorn app.main:app --port 8001`

### Docker Issues

**Image won't build:**
```bash
# Check Docker version
docker --version

# Build with verbose output
docker build -t consumesafe-api:latest . --progress=plain

# Check disk space
docker system df
```

**Container won't start:**
```bash
# View container logs
docker logs <container-id>

# Run interactively to see errors
docker run -it consumesafe-api:latest bash
```

### Kubernetes Issues

**Pod won't start:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n consumesafe

# View events
kubectl get events -n consumesafe

# Check logs
kubectl logs <pod-name> -n consumesafe
```

**Image not found error:**
```bash
# List available images in cluster
docker images

# For minikube
minikube image ls

# Load image again
minikube image load consumesafe-api:latest
```

**Port forwarding not working:**
```bash
# Verify service is running
kubectl get svc -n consumesafe

# Try port forwarding to pod directly
kubectl port-forward pod/<pod-name> 8000:8000 -n consumesafe

# Use different local port
kubectl port-forward svc/consumesafe-api 9000:8000 -n consumesafe
```

## Environment Variables

### For API
```bash
DEBUG=False                              # Debug mode
SECRET_KEY=your-secret-key              # JWT secret
DATABASE_URL=sqlite:///./test.db        # Database connection
```

### For Docker
```bash
docker run -e DEBUG=False \
           -e SECRET_KEY=your-secret \
           consumesafe-api:latest
```

### For Kubernetes
Edit `k8s/deployment.yaml` ConfigMap section:
```yaml
env:
  - name: DEBUG
    value: "False"
  - name: SECRET_KEY
    value: "your-secret-key"
```

## Performance Optimization

### Docker
- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds for smaller images
- Set resource limits

### Kubernetes
- Horizontal Pod Autoscaling (configured in deployment.yaml)
- Resource requests and limits
- Pod Disruption Budgets

### API
- Data caching on startup
- Efficient CSV processing with pandas
- Connection pooling ready

## Security Hardening

### Implemented
✅ Non-root container users
✅ Read-only root filesystems
✅ Network policies
✅ RBAC (Role-Based Access Control)
✅ Resource quotas and limits
✅ Health checks

### Recommended
- [ ] Enable HTTPS/TLS
- [ ] Configure certificate management (cert-manager)
- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Setup monitoring (Prometheus)
- [ ] Setup logging (ELK stack)
- [ ] Regular security audits

## Monitoring

### Basic Health Check
```bash
curl http://localhost:8000/api/health
```

### Kubernetes Monitoring
```bash
# View resource usage
kubectl top pods -n consumesafe
kubectl top nodes

# View metrics (requires metrics-server)
kubectl get metrics pods -n consumesafe
```

## Support

For issues, please check:
1. README.md for general information
2. This guide for deployment-specific help
3. GitHub Issues for bug reports
4. GitHub Discussions for questions

---

🇵🇸 **Stand with Palestine** 🇵🇸
Every purchase is a political choice. Support justice.
