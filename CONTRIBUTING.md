# Contributing to ConsumeSafe

We welcome contributions from anyone who wants to support this project!

## 🤝 Ways to Contribute

### 1. Add More Boycotted Products
Edit `data/boycott_products.csv` and add new rows:
```csv
51,Product Name,Brand Name,Category,Reason,Tunisian Alternative,Alternative Brand,Intensity
```

### 2. Improve the UI
- Suggest design improvements
- Report usability issues
- Create PR with CSS/HTML changes
- Add new features to frontend

### 3. Fix Bugs
- Report issues on GitHub
- Submit pull requests
- Help test new features
- Improve error handling

### 4. Improve Documentation
- Fix typos
- Add examples
- Clarify instructions
- Translate to other languages

### 5. Add Features
- New API endpoints
- Enhanced search
- Analytics
- Multi-language support
- Better alternatives algorithm

### 6. Improve Security
- Security audits
- Vulnerability reports
- Hardening suggestions
- Penetration testing

### 7. Improve Performance
- Optimize queries
- Reduce load times
- Better caching
- Database optimization

## 📝 Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ConsumeSafe.git
cd ConsumeSafe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest black flake8 isort

# Make changes
# ... edit files ...

# Run tests
pytest tests/ -v

# Check code quality
black app/
flake8 app/
isort app/

# Commit changes
git add .
git commit -m "Description of changes"
git push origin your-branch
```

## 🔄 Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write/update tests
5. Update documentation
6. Run tests: `pytest tests/ -v`
7. Check code quality: `black app/ && flake8 app/ && isort app/`
8. Commit: `git commit -m "Add amazing feature"`
9. Push: `git push origin feature/amazing-feature`
10. Create Pull Request with description

## 📝 Commit Message Guidelines

```
Type: Brief description (50 chars or less)

Longer explanation if needed (wrap at 72 chars)

- Point 1
- Point 2

Fixes #123
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Code refactor
- `test:` Test changes
- `chore:` Build/config

## 🐛 Reporting Issues

Include:
1. Description of the issue
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment (OS, Python version, etc.)
6. Screenshots/logs if applicable

## 📋 Code Style

We follow:
- PEP 8 (Python style)
- Black (formatting)
- isort (import sorting)
- flake8 (linting)

Auto-format before committing:
```bash
black app/
isort app/
```

## 🧪 Testing

Write tests for new features:

```python
def test_new_feature():
    """Test description"""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    assert "expected" in response.json()
```

Run tests:
```bash
pytest tests/ -v --cov=app
```

## 🚀 Deployment Contribution

If improving deployment:
1. Test locally first
2. Test with Docker Compose
3. Test with Kubernetes
4. Update documentation
5. Submit PR with changes

## 🔒 Security Contributions

For security issues:
1. **DO NOT** open a public issue
2. Email security@example.com with details
3. Include vulnerability type
4. Provide proof of concept if possible
5. Allow reasonable time for patching

## 📚 Documentation Contribution

- Follow Markdown syntax
- Use clear, simple language
- Include code examples
- Add section headings
- Link to related docs

## 🌍 Translation Contribution

Help translate to other languages:
1. Create new language folder: `i18n/es/`
2. Translate files
3. Test translation
4. Submit PR

## 🎓 Learning Resources

Good resources for understanding the project:
- README.md - Overview
- DEPLOYMENT.md - Deployment guide
- PROJECT_STRUCTURE.md - Architecture
- FastAPI docs: https://fastapi.tiangolo.com
- Kubernetes docs: https://kubernetes.io/docs

## 💡 Ideas & Suggestions

Have an idea?
1. Check existing issues
2. Create discussion
3. Describe feature
4. Get feedback
5. Submit PR when ready

## 🙏 Code of Conduct

- Be respectful
- Be inclusive
- Be constructive
- Support Palestinian rights
- No harassment or discrimination

## 📞 Questions?

- Check documentation
- Search existing issues
- Create discussion
- Comment on related issues

## 🎉 Thank You!

Thank you for contributing to ConsumeSafe!

Your contribution helps:
- Support Palestinian rights
- Promote ethical consumption
- Build Tunisian economy
- Create social change

Every contribution matters! 🇵🇸

---

## 🚀 Next Steps After Contributing

1. Your PR will be reviewed
2. Changes may be requested
3. Once approved, it will be merged
4. Your changes will be in next release
5. You'll be credited in CONTRIBUTORS.md

## 📊 Contributor Recognition

Contributors will be listed in:
- CONTRIBUTORS.md
- GitHub contributors page
- Release notes

---

Made with ❤️ for Palestinian Liberation

Stand with Palestine 🇵🇸
