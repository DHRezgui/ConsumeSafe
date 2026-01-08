#!/bin/bash

# ConsumeSafe Health Check Script
# Performs comprehensive health checks on deployed application

set -e

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TIMEOUT=10

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    
    response=$(curl -s -w "\n%{http_code}" --connect-timeout $TIMEOUT "$API_URL$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_status" ]; then
        log_info "$endpoint - HTTP $http_code"
        return 0
    else
        log_error "$endpoint - HTTP $http_code (expected $expected_status)"
        return 1
    fi
}

echo "====== ConsumeSafe Health Check ======"
echo ""

# API Health Checks
echo "API Endpoints:"
echo "  Base URL: $API_URL"
echo ""

passed=0
failed=0

check_endpoint "/api/health" "200" && ((passed++)) || ((failed++))
check_endpoint "/api/products" "200" && ((passed++)) || ((failed++))
check_endpoint "/api/categories" "200" && ((passed++)) || ((failed++))
check_endpoint "/api/stats" "200" && ((passed++)) || ((failed++))
check_endpoint "/api/search?query=test" "200" && ((passed++)) || ((failed++))

echo ""
echo "AI Endpoints:"
check_endpoint "/api/ai/chat" "405" && ((passed++)) || ((failed++))  # 405 because GET not allowed
check_endpoint "/api/ai/recommend" "405" && ((passed++)) || ((failed++))

echo ""
echo "Frontend:"
echo "  Base URL: $FRONTEND_URL"

if curl -s --connect-timeout $TIMEOUT "$FRONTEND_URL" > /dev/null 2>&1; then
    log_info "Frontend accessible"
    ((passed++))
else
    log_error "Frontend not accessible"
    ((failed++))
fi

echo ""
echo "====== Summary ======"
echo "Passed: $passed"
echo "Failed: $failed"

if [ $failed -eq 0 ]; then
    log_info "All checks passed!"
    exit 0
else
    log_warn "Some checks failed"
    exit 1
fi
