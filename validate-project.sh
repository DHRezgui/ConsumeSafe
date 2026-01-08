#!/bin/bash

# ConsumeSafe Project Validation & Setup Script
# Comprehensive checks to ensure everything is in place for production

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

print_header() {
    echo -e "${BLUE}====== $1 ======${NC}"
}

pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}!${NC} $1"
    ((WARNINGS++))
}

print_header "ConsumeSafe Project Validation"

# ============= PROJECT STRUCTURE =============
print_header "Project Structure"

# Check essential files
files=(
    "app/main.py"
    "app/ai_service.py"
    "app/index.html"
    "app/config.py"
    "tests/test_backend.py"
    "tests/test_ai_service.py"
    "data/boycott_products.csv"
    "docker-compose.yml"
    "Dockerfile"
    "requirements.txt"
    ".env.example"
    "k8s/deployment.yaml"
    "k8s/security.yaml"
    ".github/workflows/ci-cd.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        pass "Found: $file"
    else
        fail "Missing: $file"
    fi
done

# Check directories
directories=(
    "app"
    "data"
    "tests"
    "k8s"
    ".github"
    "logs"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        pass "Directory: $dir"
    else
        warn "Directory missing: $dir (will be created during runtime)"
    fi
done

# ============= DEPENDENCIES =============
print_header "Dependencies"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    pass "Python installed: $PYTHON_VERSION"
else
    fail "Python not installed"
fi

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    pass "Docker installed: $DOCKER_VERSION"
else
    warn "Docker not installed (required for production)"
fi

if command -v kubectl &> /dev/null; then
    KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null || echo "installed")
    pass "kubectl installed: $KUBECTL_VERSION"
else
    warn "kubectl not installed (required for Kubernetes deployment)"
fi

# ============= CODE QUALITY =============
print_header "Code Quality Checks"

if command -v python3 &> /dev/null; then
    # Check Python syntax
    if python3 -m py_compile app/main.py 2>/dev/null; then
        pass "Syntax check: app/main.py"
    else
        fail "Syntax error in app/main.py"
    fi
    
    if python3 -m py_compile app/ai_service.py 2>/dev/null; then
        pass "Syntax check: app/ai_service.py"
    else
        fail "Syntax error in app/ai_service.py"
    fi
fi

# ============= DATA & CONFIGURATION =============
print_header "Data & Configuration"

# Check CSV data
if [ -f "data/boycott_products.csv" ]; then
    line_count=$(wc -l < data/boycott_products.csv)
    pass "CSV data exists: $line_count lines"
else
    fail "CSV data file missing"
fi

# Check environment template
if [ -f ".env.example" ]; then
    pass "Environment template exists"
    
    if grep -q "API_PORT" .env.example; then
        pass "API_PORT configured in template"
    else
        fail "API_PORT not in .env.example"
    fi
    
    if grep -q "AI_ENABLED" .env.example; then
        pass "AI_ENABLED in template"
    else
        fail "AI_ENABLED not in .env.example"
    fi
else
    fail ".env.example missing"
fi

# Check for actual .env file
if [ -f ".env" ]; then
    pass "Production .env file exists"
else
    warn "Production .env not found (copy from .env.example)"
fi

# ============= API ENDPOINTS =============
print_header "API Endpoints"

# Parse main.py for endpoints
endpoints=(
    "/api/health"
    "/api/products"
    "/api/search"
    "/api/check"
    "/api/categories"
    "/api/alternatives"
    "/api/stats"
    "/api/download"
    "/api/feedback"
    "/api/ai/chat"
    "/api/ai/recommend"
    "/api/ai/analyze-sentiment"
)

for endpoint in "${endpoints[@]}"; do
    if grep -q "$endpoint" app/main.py; then
        pass "Endpoint defined: $endpoint"
    else
        fail "Endpoint missing: $endpoint"
    fi
done

# ============= AI SERVICE =============
print_header "AI Service Components"

ai_components=(
    "class AIService"
    "def chat"
    "def get_recommendations"
    "def analyze_sentiment"
)

for component in "${ai_components[@]}"; do
    if grep -q "$component" app/ai_service.py 2>/dev/null; then
        pass "AI component: $component"
    else
        fail "AI component missing: $component"
    fi
done

# ============= DOCKER CONFIGURATION =============
print_header "Docker Configuration"

if [ -f "Dockerfile" ]; then
    pass "Dockerfile exists"
    
    if grep -q "python:3.11" Dockerfile; then
        pass "Python 3.11 base image"
    else
        warn "Consider using Python 3.11"
    fi
    
    if grep -q "HEALTHCHECK" Dockerfile; then
        pass "Health check configured"
    else
        warn "No health check in Dockerfile"
    fi
else
    fail "Dockerfile missing"
fi

if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
    
    if grep -q "api:" docker-compose.yml; then
        pass "API service configured"
    else
        fail "API service not in docker-compose"
    fi
    
    if grep -q "nginx\|frontend" docker-compose.yml; then
        pass "Frontend service configured"
    else
        warn "Frontend service not configured"
    fi
else
    fail "docker-compose.yml missing"
fi

# ============= KUBERNETES CONFIGURATION =============
print_header "Kubernetes Configuration"

k8s_files=(
    "k8s/deployment.yaml"
    "k8s/security.yaml"
)

for file in "${k8s_files[@]}"; do
    if [ -f "$file" ]; then
        pass "K8s config: $file"
    else
        fail "K8s config missing: $file"
    fi
done

# Check deployment replicas
if grep -q "replicas: 2" k8s/deployment.yaml 2>/dev/null; then
    pass "Deployment replicas: 2"
else
    warn "Check deployment replicas setting"
fi

# ============= TESTING =============
print_header "Testing Framework"

test_files=(
    "tests/test_backend.py"
    "tests/test_ai_service.py"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        pass "Test file: $file"
        
        # Count test functions
        test_count=$(grep -c "def test_" "$file" 2>/dev/null || echo "0")
        pass "  Tests in $file: $test_count"
    else
        fail "Test file missing: $file"
    fi
done

# ============= CI/CD =============
print_header "CI/CD Pipeline"

if [ -f ".github/workflows/ci-cd.yml" ]; then
    pass "GitHub Actions workflow exists"
    
    if grep -q "pytest" .github/workflows/ci-cd.yml; then
        pass "Testing step configured"
    else
        warn "Testing step not in CI/CD"
    fi
    
    if grep -q "docker" .github/workflows/ci-cd.yml; then
        pass "Docker build step configured"
    else
        warn "Docker build not in CI/CD"
    fi
    
    if grep -q "trivy\|security" .github/workflows/ci-cd.yml; then
        pass "Security scanning configured"
    else
        warn "Security scanning not in CI/CD"
    fi
else
    fail "GitHub Actions workflow missing"
fi

# ============= MONITORING & LOGGING =============
print_header "Monitoring & Logging"

if [ -f "app/monitoring.py" ]; then
    pass "Monitoring module exists"
    
    if grep -q "PrometheusMetrics" app/monitoring.py; then
        pass "Prometheus metrics configured"
    else
        fail "Prometheus metrics not configured"
    fi
    
    if grep -q "JsonFormatter" app/monitoring.py; then
        pass "JSON logging configured"
    else
        fail "JSON logging not configured"
    fi
else
    fail "Monitoring module missing"
fi

# ============= DOCUMENTATION =============
print_header "Documentation"

docs=(
    "README.md"
    "PRODUCTION_GUIDE.md"
    "SECURITY.md"
    "DEPLOYMENT.md"
    "PROJECT_STRUCTURE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        pass "Documentation: $doc"
    else
        warn "Documentation missing: $doc"
    fi
done

# ============= SECURITY FILES =============
print_header "Security Configuration"

if [ -f ".gitignore" ]; then
    pass ".gitignore exists"
    
    if grep -q ".env" .gitignore; then
        pass ".env is ignored"
    else
        warn ".env should be in .gitignore"
    fi
else
    warn ".gitignore missing"
fi

# ============= SUMMARY =============
echo ""
print_header "Validation Summary"

echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Project is ready for production!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env with production values"
    echo "2. Review security settings in SECURITY.md"
    echo "3. Run tests: pytest tests/ -v"
    echo "4. Build Docker image: docker-compose build"
    echo "5. Deploy: ./deploy.sh"
    exit 0
else
    echo -e "${RED}✗ Project has issues that need to be fixed${NC}"
    echo ""
    echo "Recommended fixes:"
    if [ ! -f "tests/test_backend.py" ]; then
        echo "- Create test_backend.py"
    fi
    if [ ! -f "app/monitoring.py" ]; then
        echo "- Create monitoring.py for observability"
    fi
    if [ ! -f ".env.example" ]; then
        echo "- Create .env.example template"
    fi
    exit 1
fi
