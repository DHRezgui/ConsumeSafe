# 🚀 Guide Manuel: Docker & Kubernetes via CMD

## Prérequis Installation

```bash
# 1. Docker Desktop (avec Kubernetes intégré)
# Télécharger: https://www.docker.com/products/docker-desktop

# 2. Kubectl (client Kubernetes)
# Télécharger: https://kubernetes.io/releases/download/

# 3. Vérifier installation
docker --version
kubectl version --client
```

---

## PARTIE 1: BUILD & TEST DOCKER EN LOCAL 🐳

### Étape 1: Ouvrir Terminal CMD

```bash
# Aller au répertoire du projet
cd C:\Users\Asus\Desktop\afwa\ConsumeSafe
```

### Étape 2: Build l'image Docker

```bash
# Construire l'image Docker
docker build -t consumesafe:latest .

# Explication:
# -t consumesafe:latest = tag l'image avec le nom "consumesafe" et version "latest"
# . = utiliser le Dockerfile du répertoire courant

# Sortie attendue:
# ...
# Step 10/10 : CMD ["python", "app/main.py"]
# ---> Successfully built abc123def456
# ---> Successfully tagged consumesafe:latest
```

### Étape 3: Vérifier l'image créée

```bash
# Lister les images Docker
docker images

# Tu verras:
# REPOSITORY    TAG       IMAGE ID      CREATED       SIZE
# consumesafe   latest    abc123def456  2 minutes ago 456MB
```

### Étape 4: Lancer le container localement

```bash
# Démarrer le container
docker run -d -p 8000:8000 --name consumesafe-demo consumesafe:latest

# Explication:
# -d = détaché (run en background)
# -p 8000:8000 = mapper port 8000 host → port 8000 container
# --name = donner un nom au container
# consumesafe:latest = utiliser cette image

# Résultat: Container ID affiché (ex: a1b2c3d4e5f6)
```

### Étape 5: Vérifier que le container tourne

```bash
# Lister les containers en cours
docker ps

# Tu verras:
# CONTAINER ID   IMAGE              STATUS           PORTS
# a1b2c3d4e5f6   consumesafe:latest Up 30 seconds    0.0.0.0:8000->8000/tcp
```

### Étape 6: Tester l'application

```bash
# Tester l'API dans navigateur:
# http://localhost:8000

# Ou via CMD:
curl http://localhost:8000/api/products

# Sortie: Tous les 50 produits en JSON
```

### Étape 7: Voir les logs du container

```bash
# Afficher les logs
docker logs consumesafe-demo

# Suivi en temps réel
docker logs -f consumesafe-demo

# Tu verras:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

### Étape 8: Arrêter le container

```bash
# Arrêter le container
docker stop consumesafe-demo

# Supprimer le container
docker rm consumesafe-demo

# Vérifier qu'il est supprimé
docker ps -a
```

---

## PARTIE 2: DÉPLOIEMENT KUBERNETES 🎯

### Étape 1: Activer Kubernetes dans Docker Desktop

```bash
# Dans Docker Desktop:
# Settings → Kubernetes → Enable Kubernetes
# Attendre que le statut passe à "Kubernetes is running"

# Vérifier la connexion
kubectl cluster-info

# Sortie:
# Kubernetes master is running at https://127.0.0.1:6443
```

### Étape 2: Créer le namespace

```bash
# Créer un namespace pour notre app
kubectl create namespace consumesafe

# Vérifier
kubectl get namespaces

# Tu verras:
# NAME              STATUS
# consumesafe       Active
# default           Active
# kube-system       Active
```

### Étape 3: Créer une ConfigMap

```bash
# Créer une configmap avec les variables
kubectl create configmap consumesafe-config \
  --from-literal=APP_NAME=ConsumeSafe \
  --from-literal=ENVIRONMENT=production \
  --from-literal=DEBUG=false \
  -n consumesafe

# Vérifier
kubectl get configmaps -n consumesafe

# Afficher le contenu
kubectl describe configmap consumesafe-config -n consumesafe
```

### Étape 4: Déployer l'application

```bash
# Appliquer tous les manifests K8s
kubectl apply -f k8s/configmaps.yaml -n consumesafe
kubectl apply -f k8s/deployment.yaml -n consumesafe
kubectl apply -f k8s/services.yaml -n consumesafe

# Ou tous en une ligne:
kubectl apply -f k8s/ -n consumesafe

# Vérifier le déploiement
kubectl get deployments -n consumesafe

# Tu verras:
# NAME             READY   UP-TO-DATE   AVAILABLE
# consumesafe-api  2/2     2            2
```

### Étape 5: Vérifier les pods

```bash
# Voir tous les pods
kubectl get pods -n consumesafe

# Tu verras:
# NAME                              READY   STATUS    RESTARTS
# consumesafe-api-abc123def456-789xyz   1/1     Running   0
# consumesafe-api-abc123def456-uvwxyz   1/1     Running   0

# Détails complets
kubectl describe pod <POD_NAME> -n consumesafe

# Voir les logs d'un pod
kubectl logs <POD_NAME> -n consumesafe

# Suivi en temps réel
kubectl logs -f <POD_NAME> -n consumesafe
```

### Étape 6: Vérifier les services

```bash
# Voir les services
kubectl get services -n consumesafe

# Tu verras:
# NAME                 TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)
# consumesafe-service  ClusterIP   10.96.123.45  <none>        8000/TCP

# Détails service
kubectl describe service consumesafe-service -n consumesafe
```

### Étape 7: Port Forward pour accéder l'app

```bash
# Rediriger le port K8s vers localhost
kubectl port-forward service/consumesafe-service 8000:8000 -n consumesafe

# Maintenant accessible à:
# http://localhost:8000

# Dans une autre fenêtre CMD, tester:
curl http://localhost:8000/api/products
```

### Étape 8: Mettre à jour le déploiement

```bash
# Si tu changes le code, rebuild l'image:
docker build -t consumesafe:v1.1 .

# Met à jour le deployment
kubectl set image deployment/consumesafe-api \
  consumesafe-api=consumesafe:v1.1 \
  -n consumesafe

# Voir le rollout
kubectl rollout status deployment/consumesafe-api -n consumesafe
```

### Étape 9: Voir l'historique des déploiements

```bash
# Voir les révisions
kubectl rollout history deployment/consumesafe-api -n consumesafe

# Revenir à une version précédente (rollback)
kubectl rollout undo deployment/consumesafe-api -n consumesafe
```

### Étape 10: Supprimer tout

```bash
# Supprimer le déploiement
kubectl delete deployment consumesafe-api -n consumesafe

# Supprimer le service
kubectl delete service consumesafe-service -n consumesafe

# Supprimer la configmap
kubectl delete configmap consumesafe-config -n consumesafe

# Supprimer le namespace entier
kubectl delete namespace consumesafe

# Vérifier que c'est parti
kubectl get namespaces
```

---

## 📋 SCÉNARIO COMPLET: Montrer au Professeur

### Timing: ~15-20 minutes

```bash
# 1. BUILD (3 min)
cd C:\Users\Asus\Desktop\afwa\ConsumeSafe
docker build -t consumesafe:latest .

# 2. TEST LOCAL (2 min)
docker run -d -p 8000:8000 --name consumesafe-demo consumesafe:latest
# Ouvrir navigateur: http://localhost:8000
# Montrer que ça marche!

# 3. ARRÊTER TEST (1 min)
docker stop consumesafe-demo
docker rm consumesafe-demo

# 4. KUBERNETES SETUP (2 min)
kubectl create namespace consumesafe

# 5. DÉPLOIEMENT K8S (3 min)
kubectl apply -f k8s/ -n consumesafe
kubectl get pods -n consumesafe
kubectl get services -n consumesafe

# 6. PORT FORWARD (1 min)
kubectl port-forward service/consumesafe-service 8000:8000 -n consumesafe

# 7. TESTER VIA K8S (2 min)
# Dans nouvelle fenêtre:
curl http://localhost:8000/api/products
# Montrer navigateur: http://localhost:8000

# 8. MONTRER LES LOGS (2 min)
kubectl logs -f <POD_NAME> -n consumesafe

# 9. CLEANUP (1 min)
kubectl delete namespace consumesafe
```

---

## 🎯 Commandes Utiles Récap

### Docker
```bash
docker build -t consumesafe:latest .           # Build image
docker run -d -p 8000:8000 consumesafe:latest # Run container
docker ps                                       # List containers
docker logs <CONTAINER>                         # Voir logs
docker stop <CONTAINER>                         # Arrêter
docker rm <CONTAINER>                           # Supprimer
docker images                                   # List images
docker rmi <IMAGE>                              # Supprimer image
```

### Kubernetes
```bash
kubectl create namespace consumesafe           # Créer namespace
kubectl apply -f k8s/                          # Déployer
kubectl get pods -n consumesafe                # Voir pods
kubectl get services -n consumesafe            # Voir services
kubectl describe pod <POD> -n consumesafe      # Détails
kubectl logs <POD> -n consumesafe              # Logs
kubectl port-forward svc/NAME 8000:8000        # Port forward
kubectl delete namespace consumesafe           # Supprimer tout
kubectl rollout status deployment/NAME         # Voir rollout
```

---

## ✅ Checklist Professeur

- [ ] Application démarre (docker run)
- [ ] API répond (/api/products)
- [ ] Interface web accessible
- [ ] Déploiement K8s successful
- [ ] Pods running (2 replicas)
- [ ] Service accessible via port-forward
- [ ] Logs visibles et clairs
- [ ] Récupération simple des images/pods

---

## 🎓 Points à Expliquer au Professeur

1. **Docker** - Containerize l'app, reproductibilité
2. **Image vs Container** - Image = template, Container = instance
3. **Ports** - 8000 host mapped à 8000 container
4. **Kubernetes** - Orchestration, scaling automatique
5. **Namespace** - Isolation des ressources
6. **Deployment** - Gère les pods, replicasets
7. **Service** - Expose l'app network
8. **Health Checks** - K8s redémarre si échoue

---

✅ **Tu as tout pour montrer une démo complète et professionnelle!**
