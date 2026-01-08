ConsumeSafe/
├── 📂 app/                          # Application principale
│   ├── 🐍 main.py                  # API FastAPI (12 endpoints)
│   ├── 🐍 config.py                # Configuration
│   ├── 🐍 __init__.py              # Package init
│   └── 🌐 index.html               # Frontend UI (Tailwind CSS)
│
├── 📂 data/                         # Données
│   └── 📊 boycott_products.csv     # 50+ produits boycottés + alternatives
│
├── 📂 tests/                        # Tests unitaires
│   ├── 🐍 test_api.py             # Tests FastAPI (17 test cases)
│   └── 🐍 __init__.py
│
├── 📂 k8s/                          # Kubernetes manifests
│   ├── 📋 deployment.yaml          # Deployments + Services + HPA
│   ├── 🔒 security.yaml            # RBAC + Network Policies + Quotas
│   ├── 🌐 ingress.yaml             # Ingress + TLS
│   └── ⚙️  configmaps.yaml         # ConfigMaps pour HTML/Nginx
│
├── 📂 .github/workflows/            # CI/CD Pipeline
│   └── 📋 ci-cd.yml                # GitHub Actions workflow
│
├── 🐳 Dockerfile                    # Image Docker Python
├── 🐳 docker-compose.yml            # Docker Compose (API + Frontend)
├── 📝 nginx.conf                    # Configuration Nginx
├── 📝 requirements.txt              # Python dependencies
├── 📝 README.md                     # Guide principal
├── 📝 DEPLOYMENT.md                 # Guide de déploiement
├── 📝 .gitignore                    # Fichiers ignorés Git
├── 🚀 quickstart.py                 # Script de démarrage rapide
└── 🚀 deploy.sh / deploy.bat        # Scripts de déploiement

═══════════════════════════════════════════════════════════════════

📊 STATISTICS
═══════════════════════════════════════════════════════════════════

🔧 Backend (API)
  • FastAPI server avec 12 endpoints
  • Pandas pour le traitement CSV
  • Health checks et logging intégrés
  • CORS configuré
  • Validation avec Pydantic

🎨 Frontend
  • HTML5 moderne
  • Tailwind CSS responsive
  • Font Awesome icons
  • JavaScript vanilla (pas de framework lourd)
  • Mode sombre persuasif avec couleurs Palestine

📦 Dataset
  • 50+ produits boycottés
  • Marques internationales (Nestlé, PepsiCo, Microsoft, etc.)
  • Alternatives tunisiennes proposées
  • 3 niveaux d'intensité (High, Medium, Low)
  • Raisons de boycott détaillées

🧪 Tests
  • 17 test cases unitaires
  • Coverage sur tous les endpoints
  • Tests d'intégration API
  • Configuration pytest

🐳 Docker
  • Alpine slim image
  • Non-root user (1000)
  • Health checks
  • Volume pour données persistantes
  • Nginx reverse proxy

☸️  Kubernetes
  • Namespace isolé
  • 2 déploiements (API + Frontend)
  • Services ClusterIP + LoadBalancer
  • Horizontal Pod Autoscaler (2-5 replicas)
  • Pod Disruption Budget
  • Network Policies
  • RBAC
  • Resource Quotas & Limits
  • Ingress avec TLS ready

🔐 Sécurité
  ✅ Non-root containers (UID 1000)
  ✅ Read-only root filesystems
  ✅ No privilege escalation
  ✅ No dangerous capabilities
  ✅ RBAC policies
  ✅ Network policies
  ✅ Resource limits
  ✅ Pod Disruption Budgets
  ✅ TLS/HTTPS ready
  ✅ Rate limiting ready (nginx)

🔄 CI/CD
  • GitHub Actions workflow
  • Multi-version Python testing (3.10, 3.11)
  • Code quality checks (flake8, black, isort)
  • Security scanning (Trivy)
  • Docker image build & push
  • Kubernetes deployment automation
  • Coverage reports to Codecov

═══════════════════════════════════════════════════════════════════

🚀 QUICK START COMMANDS
═══════════════════════════════════════════════════════════════════

Local Development:
  $ python quickstart.py
  # Opens http://localhost:8080 automatically

Docker Compose:
  $ docker-compose up -d
  # Frontend: http://localhost:3000
  # API: http://localhost:8000

Kubernetes:
  $ ./deploy.sh          # Linux/Mac
  $ deploy.bat          # Windows
  # Or manually:
  $ kubectl apply -f k8s/
  $ kubectl port-forward svc/consumesafe-frontend 3000:80 -n consumesafe

═══════════════════════════════════════════════════════════════════

🔗 API ENDPOINTS
═══════════════════════════════════════════════════════════════════

GET  /                                    # Root info
GET  /api/health                         # Health check
GET  /api/check?product_name=<name>      # Check if boycotted
GET  /api/alternatives?product_name=<name> # Get alternatives
GET  /api/boycotts                       # List all products
GET  /api/categories                     # Get categories
GET  /api/stats                          # Statistics
GET  /api/search?q=<query>               # Search products
GET  /api/download/boycott_list.csv      # Download CSV
GET  /api/message                        # Random solidarity message
POST /api/feedback                       # Submit feedback

Swagger UI: http://localhost:8000/docs

═══════════════════════════════════════════════════════════════════

📋 PROJECT FEATURES
═══════════════════════════════════════════════════════════════════

✨ Core Features
  ✅ Check if product is boycotted
  ✅ Get Tunisian alternatives automatically
  ✅ Download full boycott list as CSV
  ✅ View statistics by category/intensity
  ✅ Search functionality
  ✅ Feedback collection

🎯 UI Features
  ✅ Responsive design (mobile/tablet/desktop)
  ✅ Dark theme with Palestine colors
  ✅ Persuasive messaging
  ✅ Smooth animations
  ✅ Tab navigation
  ✅ Real-time solidarity messages
  ✅ Product cards with rich information
  ✅ Alternative suggestions highlighted

🔧 Technical Features
  ✅ REST API with FastAPI
  ✅ CORS enabled
  ✅ Error handling
  ✅ Rate limiting ready
  ✅ Health checks
  ✅ Logging
  ✅ CSV handling
  ✅ JSON responses

📦 Deployment Features
  ✅ Docker containerization
  ✅ Docker Compose setup
  ✅ Kubernetes orchestration
  ✅ High availability (replicas)
  ✅ Auto-scaling
  ✅ Health probes
  ✅ Resource management
  ✅ Persistent storage

🔒 Security Features
  ✅ Non-root users
  ✅ Read-only filesystems
  ✅ Network policies
  ✅ RBAC
  ✅ Resource quotas
  ✅ No privilege escalation
  ✅ Minimal attack surface
  ✅ Security scanning in CI/CD

🧪 Quality Features
  ✅ Unit tests (17 cases)
  ✅ Code quality checks
  ✅ Security scanning
  ✅ Linting
  ✅ Code formatting
  ✅ CI/CD automation
  ✅ Test coverage tracking

═══════════════════════════════════════════════════════════════════

🇵🇸 SOLIDARITY MESSAGE
═══════════════════════════════════════════════════════════════════

This application stands with the Palestinian people in their struggle 
for freedom, dignity, and self-determination.

By using ConsumeSafe, you:
  • Make informed consumption choices
  • Support Palestinian rights
  • Strengthen Tunisian economy
  • Send a message to corporations
  • Participate in the BDS movement
  
Every purchase IS a political choice.
Free Palestine from the river to the sea.

═══════════════════════════════════════════════════════════════════

Made with ❤️ for Palestinian liberation and Tunisian pride

For updates and contribution: https://github.com/yourusername/ConsumeSafe
