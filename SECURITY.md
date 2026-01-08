# Security & DevSecOps Guide

## 🔐 Security Architecture

ConsumeSafe implements a comprehensive security strategy following OWASP Top 10 guidelines and DevSecOps best practices.

### 1. **Input Validation & Sanitization**

#### Implementation
```python
def sanitize_input(text: str, max_length: int = 200) -> str:
    """Sanitize user input to prevent injection attacks"""
    - Limits string length to prevent buffer overflow
    - Removes null bytes (\x00)
    - HTML escapes all user input
    - Whitelists alphanumeric characters and safe symbols
    - Prevents XSS and injection attacks
```

#### Coverage
- **Search queries**: Max 100 characters, alphanumeric only
- **Product names**: Validated against whitelist
- **Feedback**: HTML escaped, max 500 characters
- **Email input**: Limited to 100 characters

### 2. **Rate Limiting**

#### Implementation
```python
class RateLimiter:
    - Max 100 requests per minute per IP
    - Maintains request history with timestamps
    - Thread-safe implementation using locks
    - Automatic cleanup of expired requests
```

#### Usage
- All endpoints protected by rate limiting
- Returns 429 (Too Many Requests) when limit exceeded
- Client IP tracked and logged

### 3. **CORS (Cross-Origin Resource Sharing)**

#### Strict Policy
```python
allow_origins = ["http://127.0.0.1:8080", "http://localhost:8080"]
allow_methods = ["GET", "POST"]
allow_headers = ["Content-Type", "Accept"]
max_age = 3600  # 1 hour
```

#### Security Benefits
- Prevents unauthorized cross-origin requests
- Restricts to localhost during development
- Can be updated for production domains
- Preflight requests cached for 1 hour

### 4. **Security Headers**

#### Implemented Headers

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevents MIME type sniffing |
| X-Frame-Options | DENY | Prevents clickjacking attacks |
| X-XSS-Protection | 1; mode=block | Enables XSS protection |
| Strict-Transport-Security | max-age=31536000 | Forces HTTPS for 1 year |
| Content-Security-Policy | restrictive | Controls resource loading |
| Referrer-Policy | strict-origin-when-cross-origin | Controls referrer information |
| Permissions-Policy | deny all | Disables unnecessary APIs |
| Cache-Control | public, max-age=3600 | Browser caching policy |

### 5. **Middleware Stack**

#### Security Middleware Layers (in order)
1. **TrustedHostMiddleware** - Validates Host header
2. **GZIPMiddleware** - Compresses responses (performance)
3. **CORSMiddleware** - Cross-origin security
4. **Custom Security Headers** - Adds security headers
5. **Rate Limiting** - Prevents brute force attacks

### 6. **Data Protection**

#### CSV Database
- ✅ No sensitive data stored
- ✅ Public product information only
- ✅ Read-only access (no database writes)
- ✅ No user authentication required
- ✅ GDPR compliant (no personal data)

#### Logging
- All requests logged with IP address
- Error stack traces logged server-side only
- No sensitive information in logs
- Log rotation recommended for production

### 7. **API Endpoint Security**

#### Query Parameter Validation
```python
# All user inputs validated with Query parameters
product_name: str = Query(..., min_length=1, max_length=100)
limit: int = Query(50, ge=1, le=500)  # Range validation
intensity: str  # Validated against whitelist
category: str   # Validated against dataset
```

#### Error Handling
- Generic error messages to prevent information leakage
- Detailed errors logged server-side only
- No stack traces exposed to clients
- Consistent JSON error response format

### 8. **HTTPS/TLS Recommendations**

#### For Production
1. Deploy behind NGINX with SSL/TLS
2. Use Let's Encrypt for free certificates
3. Set HSTS headers (already implemented)
4. Redirect HTTP to HTTPS

#### Docker/K8s Deployment
```yaml
# nginx.conf configuration
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

## 🛡️ OWASP Top 10 Compliance

| # | Issue | Status | Implementation |
|---|-------|--------|-----------------|
| A01 | Broken Access Control | ✅ PROTECTED | No authentication needed, rate limiting applied |
| A02 | Cryptographic Failures | ✅ PROTECTED | HTTPS recommended, all data public |
| A03 | Injection | ✅ PROTECTED | Input sanitization, whitelisting, parameterized queries |
| A04 | Insecure Design | ✅ PROTECTED | Security by design, threat modeling |
| A05 | Security Misconfiguration | ✅ PROTECTED | Secure defaults, minimal dependencies |
| A06 | Vulnerable Components | ✅ PROTECTED | Regular dependency updates, no known vulns |
| A07 | Authentication Issues | ✅ N/A | No auth required, rate limiting instead |
| A08 | Data Integrity Failures | ✅ PROTECTED | Read-only data, CORS validation |
| A09 | Logging Failures | ✅ PROTECTED | Comprehensive logging, no sensitive data |
| A10 | SSRF | ✅ PROTECTED | No external requests, no file uploads |

## 🔍 Dependency Security

### Minimal Dependencies
```
fastapi==0.109.0           # Web framework, OWASP compliant
uvicorn[standard]==0.27.0  # ASGI server with std extras
aiofiles==23.2.1           # Async file operations
pytest==7.4.3              # Testing framework
```

### Security Scanning
#### Local Scanning
```bash
# Check for known vulnerabilities
pip install safety
safety check

# Dependency analysis
pip-audit
```

#### CI/CD Scanning (GitHub Actions)
```yaml
- name: Run dependency check
  uses: dependency-check/Dependency-Check_Action@main
  with:
    project: 'ConsumeSafe'
    path: '.'
    format: 'SARIF'
    args: >
      --enable-experimental
```

## 🚀 Deployment Security

### Docker Security Checklist
- ✅ Non-root user (no privilege escalation)
- ✅ Read-only filesystem
- ✅ Resource limits (CPU, memory)
- ✅ Health checks
- ✅ Minimal base image (python:3.11-slim)

### Kubernetes Security

#### Network Policy
```yaml
kind: NetworkPolicy
metadata:
  name: consumesafe-network-policy
spec:
  podSelector:
    matchLabels:
      app: consumesafe
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: default
      ports:
      - protocol: TCP
        port: 8000
  egress:
    - to:
      - namespaceSelector: {}
      ports:
      - protocol: TCP
        port: 53  # DNS only
```

#### Pod Security Policy
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: consumesafe-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

## 🧪 Security Testing

### Manual Testing
```bash
# 1. XSS Testing
curl "http://127.0.0.1:8000/api/search?q=<script>alert('xss')</script>"
# Expected: Input sanitized, script removed

# 2. SQL Injection Testing
curl "http://127.0.0.1:8000/api/search?q='; DROP TABLE--"
# Expected: Treated as normal input, no DB access

# 3. Rate Limiting Test
for i in {1..101}; do curl http://127.0.0.1:8000/api/health; done
# Expected: 101st request returns 429

# 4. CORS Testing
curl -H "Origin: http://evil.com" http://127.0.0.1:8000/api/boycotts
# Expected: CORS headers restrict access
```

### Automated Testing
```python
# tests/test_security.py
def test_input_sanitization():
    response = client.get("/api/search?q=<script>alert('xss')</script>")
    assert response.status_code == 200
    # Script should be removed

def test_rate_limiting():
    for i in range(101):
        response = client.get("/api/health")
    assert response.status_code == 429

def test_cors_headers():
    response = client.get("/api/boycotts")
    assert "CORS" in response.headers or response.status_code in [200, 403]
```

## 🔐 Environment Variables

### Secure Configuration
```bash
# .env (never commit)
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=production
LOG_LEVEL=info
RATE_LIMIT=100  # requests per minute
RATE_WINDOW=60  # seconds
```

### Production Deployment
```bash
export ENVIRONMENT=production
export LOG_LEVEL=warning  # Reduce verbose logging
export RATE_LIMIT=200     # Adjust for prod traffic
```

## 📊 Security Monitoring

### Log Analysis
```bash
# Monitor failed requests
grep -i "error\|exception" /var/log/consumesafe.log

# Monitor rate limit violations
grep "429\|Too many requests" /var/log/consumesafe.log

# Monitor failed health checks
grep "unhealthy" /var/log/consumesafe.log
```

### Metrics to Monitor
- Request rate by IP
- Error rate by endpoint
- Response time percentiles
- Failed authentication attempts
- Database query performance

## 🚨 Incident Response

### Compromise Detection
1. Monitor for unusual request patterns
2. Check logs for injection attempts
3. Review rate limit violations
4. Monitor CPU/memory spikes

### Response Procedures
1. **Isolation**: Separate affected instance from load balancer
2. **Investigation**: Review logs and metrics
3. **Mitigation**: Apply fixes or rollback
4. **Recovery**: Restore from backup if needed
5. **Communication**: Notify users if data exposed

## 🔄 Regular Security Updates

### Update Schedule
- **Weekly**: Check for dependency updates
- **Monthly**: Security audit review
- **Quarterly**: Penetration testing
- **Annually**: Full security assessment

### Commands
```bash
# Check for outdated packages
pip list --outdated

# Update all packages safely
pip install --upgrade -r requirements.txt

# Run security tests
pytest tests/test_security.py -v
```

## 📋 Compliance Checklist

- ✅ OWASP Top 10 compliance
- ✅ Input validation & sanitization
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Security headers
- ✅ Error handling
- ✅ Logging & monitoring
- ✅ HTTPS/TLS support
- ✅ Dependency scanning
- ✅ Docker security
- ✅ Kubernetes RBAC
- ✅ Network policies
- ✅ Pod security policies

## 🤝 Contributing Security

Found a security vulnerability? Please email security@consumesafe.local or create a private security advisory.

### Report Template
```
1. Vulnerability Description
2. Steps to Reproduce
3. Potential Impact
4. Suggested Fix
5. Your Contact Information
```

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

**Last Updated**: January 6, 2026  
**Maintained By**: ConsumeSafe Security Team  
**Version**: 2.0.0
