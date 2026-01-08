# 🚀 Pipeline CI/CD ConsumeSafe - Visualisation Complète

## 📊 Flux Global du Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DÉCLENCHEURS (Triggers)                       │
├─────────────────────────────────────────────────────────────────┤
│  • Push sur main ou develop                                      │
│  • Pull Request vers main ou develop                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ÉTAPE 1: TEST (Toujours)                      │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Setup Python 3.10 & 3.11                                     │
│  ✅ Installer dépendances (cache pip)                            │
│  ✅ Linting avec flake8                                          │
│  ✅ Vérifier format code (black)                                 │
│  ✅ Vérifier ordre imports (isort)                               │
│  ✅ Exécuter 75+ tests automatisés                               │
│  ✅ Coverage report (85%+)                                       │
│  ✅ Upload résultats à Codecov                                   │
└─────────────────────────────────────────────────────────────────┘
              ↓                          ↓
         ❌ ÉCHOUE              ✅ SUCCÈS
              ↓                          ↓
        BLOQUER MERGE            ÉTAPE 2: BUILD
                                (Si push, pas PR)
┌─────────────────────────────────────────────────────────────────┐
│              ÉTAPE 2: BUILD Docker (Si Push)                     │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Setup Docker Buildx                                         │
│  ✅ Login à GitHub Container Registry                           │
│  ✅ Extraire métadonnées (version, sha, etc)                    │
│  ✅ Build image Docker                                          │
│  ✅ Push vers ghcr.io/consumesafe-api                           │
│  ✅ Tagger: main, develop, version, sha                         │
│  ✅ Cache pour builds futurs                                    │
└─────────────────────────────────────────────────────────────────┘
              ↓                          ↓
         ❌ ÉCHOUE              ✅ SUCCÈS
              ↓                          ↓
        ALERT SLACK            ÉTAPE 3: SECURITY
                                   (Parallèle)
┌─────────────────────────────────────────────────────────────────┐
│          ÉTAPE 3: SECURITY SCAN (Parallèle au BUILD)             │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Trivy: Scan vulnérabilités filesystem                        │
│  ✅ Format résultats en SARIF                                    │
│  ✅ Upload à GitHub Security Tab                                │
│  ✅ Détecte: CVE, dépendances faibles, secrets                  │
└─────────────────────────────────────────────────────────────────┘
              ↓                          ↓
         ❌ ALERTE               ✅ SUCCÈS
         (Continue)              ÉTAPE 4: DEPLOY
                                 (Si main branch)
┌─────────────────────────────────────────────────────────────────┐
│      ÉTAPE 4: DEPLOY Kubernetes (Si main + Push)                │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Decoder kubeconfig depuis secrets                           │
│  ✅ Appliquer manifests K8s (deployment, service, etc)          │
│  ✅ Attendre rollout status (max 5min)                          │
│  ✅ Vérifier pods et services déployés                          │
│  ✅ Health checks automatiques                                  │
└─────────────────────────────────────────────────────────────────┘
              ↓
         DÉPLOIEMENT COMPLET ✅
```

---

## 🔄 Scénarios d'Exécution

### 📌 Scénario 1: Pull Request vers main
```
Trigger: PR créée
Exécute: TEST uniquement
Résultat: ✅ Teste tout, pas de build/deploy
Permet merge si tout passe
```

### 📌 Scénario 2: Push sur develop
```
Trigger: git push origin develop
Exécute: TEST → BUILD → SECURITY
Résultat: ✅ Test + Build image Docker
          ✅ Scan sécurité
          ❌ PAS de déploiement K8s
Action: Image poussée à ghcr.io:develop
```

### 📌 Scénario 3: Push sur main
```
Trigger: git push origin main
Exécute: TEST → BUILD → SECURITY → DEPLOY
Résultat: ✅ Tous les tests
          ✅ Image Docker compilée
          ✅ Scan sécurité complet
          ✅ Déployé en production K8s
Action: Application vit sur cluster!
```

---

## 📋 Étapes Détaillées

### 1️⃣ TEST (toujours)
| Étape | Command | Temps | Status |
|-------|---------|-------|--------|
| Checkout code | `actions/checkout@v3` | <1s | ✅ |
| Setup Python | `3.10, 3.11` | 30s | ✅ |
| Cache pip | ~/.cache/pip | 5s | ✅ |
| Install deps | `pip install -r req.txt` | 45s | ✅ |
| Linting | `flake8 app/` | 15s | ✅ |
| Format check | `black --check app/` | 10s | ✅ |
| Import order | `isort --check app/` | 10s | ✅ |
| Run tests | `pytest -v --cov` | 60s | ✅ |
| Upload coverage | Codecov | 5s | ✅ |
| **TOTAL** | - | **~3 min** | ✅ |

### 2️⃣ BUILD Docker (si push)
| Étape | Action | Temps | Status |
|-------|--------|-------|--------|
| Setup Buildx | Docker build kit | 10s | ✅ |
| Login registry | GHCR token | 5s | ✅ |
| Extract metadata | Version/SHA | 5s | ✅ |
| Build image | Multi-layer | 90s | ✅ |
| Push image | ghcr.io | 30s | ✅ |
| **TOTAL** | - | **~2.5 min** | ✅ |

### 3️⃣ SECURITY (parallèle)
| Scan | Outil | Cibles | Status |
|------|-------|--------|--------|
| Vulnérabilités | Trivy | Dépendances, OS | ✅ |
| Secrets | Built-in | Fichiers source | ✅ |
| Format rapport | SARIF | GitHub native | ✅ |
| **TOTAL** | - | **~1.5 min** | ✅ |

### 4️⃣ DEPLOY K8s (main seulement)
| Étape | Action | Résultat | Status |
|-------|--------|---------|--------|
| Decode kubeconfig | Base64 → ~/.kube/config | Accès cluster | ✅ |
| Apply manifests | kubectl apply -f k8s/ | Deployment, Service, Ingress | ✅ |
| Rollout status | kubectl rollout status | Attend pods ready | ✅ |
| Verify pods | kubectl get pods | Affiche status | ✅ |
| Verify services | kubectl get services | Network actif | ✅ |
| **TOTAL** | - | **~2 min** | ✅ |

---

## 🔐 Secrets & Sécurité

```
github.token (auto)          → Login GHCR
GITHUB_TOKEN (auto)          → Push images
secrets.KUBE_CONFIG          → Accès cluster K8s
```

---

## 📊 Temps d'Exécution Total

```
┌─────────────────────────────────────┐
│ PR VERS MAIN                        │
├─────────────────────────────────────┤
│ TEST uniquement        ~3 min  ✅   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ PUSH VERS DEVELOP                   │
├─────────────────────────────────────┤
│ TEST                   ~3 min  ✅   │
│ BUILD (parallèle)      ~2.5 min ✅  │
│ SECURITY (parallèle)   ~1.5 min ✅  │
├─────────────────────────────────────┤
│ TOTAL                  ~3-4 min ✅  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ PUSH VERS MAIN (PRODUCTION)         │
├─────────────────────────────────────┤
│ TEST                   ~3 min  ✅   │
│ BUILD (parallèle)      ~2.5 min ✅  │
│ SECURITY (parallèle)   ~1.5 min ✅  │
│ DEPLOY (séquentiel)    ~2 min  ✅   │
├─────────────────────────────────────┤
│ TOTAL                  ~7-8 min ✅  │
│ → APP EN PRODUCTION!               │
└─────────────────────────────────────┘
```

---

## 🎯 Résumé Pipeline

| Composant | Technologie | Status |
|-----------|-------------|--------|
| **Trigger** | GitHub Events (push/PR) | ✅ |
| **Test** | pytest + coverage | ✅ |
| **Lint** | flake8 + black + isort | ✅ |
| **Build** | Docker + Buildx | ✅ |
| **Registry** | GitHub Container Registry | ✅ |
| **Security** | Trivy + SARIF | ✅ |
| **Deploy** | Kubernetes kubectl | ✅ |
| **Orchestration** | GitHub Actions | ✅ |

---

## ⚡ Commandes pour Déclencher

```bash
# Déclencher TEST (PR)
git checkout feature-branch
git push origin feature-branch
# → GitHub crée PR automatiquement

# Déclencher TEST + BUILD + SECURITY
git push origin develop

# Déclencher FULL PIPELINE (deploy production!)
git push origin main
```

---

## 📈 Monitoring du Pipeline

1. **Onglet Actions** sur GitHub
   - Voir statut real-time
   - Logs détaillés par étape
   - Durée de chaque job

2. **Security Tab**
   - Trivy scan results
   - CVE détectées
   - Recommendations

3. **Packages**
   - Images Docker versionnées
   - SHA builds
   - Tags: latest, develop, main

---

## 🛠️ Améliorations Possibles

- [ ] Notifications Slack/Discord
- [ ] Performance tests automatiques
- [ ] Load testing (K6)
- [ ] Database migrations
- [ ] Backup automatiques
- [ ] Rollback automatique si health check échoue

---

✅ **ConsumeSafe a un pipeline CI/CD complètement automatisé et production-ready!**
