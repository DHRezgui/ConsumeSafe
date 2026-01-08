# ConsumeSafe - Boycott Awareness Application

**Stand with Palestine 🇵🇸 | Support Tunisia 🇹🇳**

A comprehensive application to check if products are on the boycott list and find Tunisian alternatives. Powered by BDS (Boycott, Divestment, Sanctions) principles.

## Features

✅ **Product Search** - Check if a product is boycotted
✅ **Tunisian Alternatives** - Find local alternatives automatically
✅ **CSV Export** - Download the complete boycott list
✅ **Statistics** - View boycott data by category and intensity
✅ **Beautiful UI** - Persuasive interface to encourage ethical consumption
✅ **REST API** - Full API for integration
✅ **Docker** - Container support for easy deployment
✅ **Kubernetes** - K8S manifests for scalable deployment
✅ **CI/CD** - GitHub Actions pipeline
✅ **Security** - JWT, rate limiting, RBAC, network policies

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/ConsumeSafe.git
cd ConsumeSafe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
python -m uvicorn app.main:app --reload

# In another terminal, serve the frontend
python -m http.server 8080 --directory app
```

Visit:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8080

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
```

### Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n consumesafe
kubectl get services -n consumesafe

# Port forward to access locally
kubectl port-forward svc/consumesafe-frontend 3000:80 -n consumesafe
kubectl port-forward svc/consumesafe-api 8000:8000 -n consumesafe
```

## API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/check?product_name=<name>` - Check if product is boycotted
- `GET /api/alternatives?product_name=<name>` - Get Tunisian alternatives
- `GET /api/boycotts` - List all boycotted products
- `GET /api/categories` - Get product categories
- `GET /api/stats` - Get statistics
- `GET /api/search?q=<query>` - Search products
- `GET /api/download/boycott_list.csv` - Download CSV
- `GET /api/message` - Get solidarity message
- `POST /api/feedback` - Submit feedback

## Dataset

The `data/boycott_products.csv` contains:
- **50+ boycotted products** from international brands
- **Reasons for boycott** (Israeli settlements, military support, etc.)
- **Tunisian alternatives** for each product
- **Intensity levels** (High, Medium, Low)
- **Categories** (Beverages, Food, Electronics, etc.)

## Technology Stack

- **Backend**: Python, FastAPI, Pandas, Uvicorn
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Container**: Docker, Docker Compose
- **Orchestration**: Kubernetes (K8S)
- **CI/CD**: GitHub Actions
- **Security**: RBAC, Network Policies, SSL/TLS

## Security Features

- ✅ Non-root container users
- ✅ Read-only root filesystems
- ✅ Resource quotas and limits
- ✅ Network policies
- ✅ RBAC (Role-Based Access Control)
- ✅ Pod Disruption Budgets
- ✅ Health checks and probes
- ✅ Secret management ready
- ✅ Rate limiting (via nginx/ingress)
- ✅ CORS protection

## BDS Movement

**Boycott, Divestment, Sanctions (BDS)** is a Palestinian-led movement for human rights and justice.

It calls for:
1. **Boycott** - Avoid companies supporting Israeli occupation
2. **Divestment** - Remove investments from complicit companies
3. **Sanctions** - Pressure governments for sanctions

### Why BDS?

Palestinian people have the right to:
- Self-determination
- Freedom from occupation
- Protection of human rights
- Repatriation of refugees

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Database Updates

To add new products to the boycott list, edit `data/boycott_products.csv`:

```csv
id,boycott_product,brand,category,reason,tunisian_alternative,alternative_brand,intensity
51,New Product,Brand Name,Category,Reason for boycott,Tunisian Alternative,Brand,High/Medium/Low
```

## Deployment

### Environment Variables

```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=sqlite:///./test.db
```

### CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Runs tests (Python 3.10, 3.11)
2. Checks code quality (flake8, black, isort)
3. Builds Docker image
4. Scans for vulnerabilities (Trivy)
5. Deploys to Kubernetes (on main branch)

## License

MIT License - See LICENSE file for details

## Solidarity

🇵🇸 **Free Palestine from the river to the sea**

This project stands with the Palestinian people in their struggle for freedom, dignity, and self-determination.

---

Made with ❤️ for Palestinian liberation and Tunisian pride

*"Every purchase is a political choice. Choose Palestine. Choose Justice."*
