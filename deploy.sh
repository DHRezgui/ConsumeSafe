#!/bin/bash

# ConsumeSafe Deployment Script

set -e

echo "🇵🇸 ConsumeSafe - Deployment Script"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="consumesafe"
DOCKER_IMAGE="consumesafe-api:latest"
DEPLOYMENT_NAME="consumesafe-api"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { print_error "Docker is not installed"; exit 1; }
print_success "Docker is installed"

command -v kubectl >/dev/null 2>&1 || print_warning "kubectl is not installed"
command -v docker-compose >/dev/null 2>&1 || print_warning "docker-compose is not installed"

# Check if running locally or on K8S
echo ""
echo "Deployment options:"
echo "1) Docker Compose (Local)"
echo "2) Kubernetes (Cluster)"
echo "3) Both"

read -p "Choose deployment option (1-3): " deployment_choice

# Docker Compose Deployment
if [ "$deployment_choice" = "1" ] || [ "$deployment_choice" = "3" ]; then
    echo ""
    echo "Starting Docker Compose deployment..."
    
    # Build images
    print_warning "Building Docker images..."
    docker-compose build
    print_success "Docker images built"
    
    # Start services
    print_warning "Starting services..."
    docker-compose up -d
    print_success "Services started"
    
    # Wait for services to be healthy
    echo "Waiting for services to be healthy..."
    sleep 10
    
    # Test API
    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_success "API is healthy"
        echo ""
        echo "Docker Compose Deployment Complete!"
        echo "Access the application at:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
    else
        print_error "API health check failed"
        docker-compose logs
        exit 1
    fi
fi

# Kubernetes Deployment
if [ "$deployment_choice" = "2" ] || [ "$deployment_choice" = "3" ]; then
    echo ""
    echo "Starting Kubernetes deployment..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is required for K8S deployment"
        exit 1
    fi
    
    # Create namespace
    print_warning "Creating namespace..."
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    print_success "Namespace created/updated"
    
    # Build Docker image
    print_warning "Building Docker image..."
    docker build -t $DOCKER_IMAGE .
    print_success "Docker image built"
    
    # Load image into K8S (if using kind/minikube)
    if kubectl config current-context | grep -q "kind\|minikube"; then
        print_warning "Loading image into K8S cluster..."
        if command -v kind &> /dev/null; then
            kind load docker-image $DOCKER_IMAGE
        elif command -v minikube &> /dev/null; then
            eval $(minikube docker-env)
            docker build -t $DOCKER_IMAGE .
        fi
        print_success "Image loaded"
    fi
    
    # Apply manifests
    print_warning "Applying Kubernetes manifests..."
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/security.yaml
    print_success "Manifests applied"
    
    # Wait for deployment
    print_warning "Waiting for deployment to be ready..."
    kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=5m
    print_success "Deployment is ready"
    
    # Get service info
    echo ""
    echo "Kubernetes Deployment Complete!"
    echo "Cluster Services:"
    kubectl get services -n $NAMESPACE
    
    # Port forwarding instructions
    echo ""
    echo "To access the application locally, use port forwarding:"
    echo "  kubectl port-forward svc/consumesafe-frontend 3000:80 -n $NAMESPACE"
    echo "  kubectl port-forward svc/consumesafe-api 8000:8000 -n $NAMESPACE"
fi

echo ""
echo "🇵🇸 ConsumeSafe is ready to serve!"
echo "Remember: Every purchase is a political choice."
echo "Stand with Palestine. Support Tunisia."
