@echo off
REM ConsumeSafe Deployment Script for Windows

echo 🇵🇸 ConsumeSafe - Windows Deployment Script
echo ==========================================

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not installed
    exit /b 1
)
echo ✓ Docker is installed

REM Menu
echo.
echo Deployment options:
echo 1) Docker Compose (Local)
echo 2) Kubernetes (Cluster)
echo 3) Both
echo.
set /p deployment_choice="Choose deployment option (1-3): "

if "%deployment_choice%"=="1" goto docker_compose
if "%deployment_choice%"=="2" goto kubernetes
if "%deployment_choice%"=="3" goto both
echo Invalid choice
exit /b 1

:docker_compose
echo.
echo Starting Docker Compose deployment...
docker-compose build
docker-compose up -d
echo.
echo Waiting for services...
timeout /t 10 /nobreak
echo.
echo Docker Compose Deployment Complete!
echo Access the application at:
echo   - Frontend: http://localhost:3000
echo   - API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
exit /b 0

:kubernetes
echo.
echo Starting Kubernetes deployment...
echo Building Docker image...
docker build -t consumesafe-api:latest .
echo Applying Kubernetes manifests...
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/security.yaml
echo.
echo Kubernetes Deployment Complete!
echo Run these commands for port forwarding:
echo   kubectl port-forward svc/consumesafe-frontend 3000:80 -n consumesafe
echo   kubectl port-forward svc/consumesafe-api 8000:8000 -n consumesafe
exit /b 0

:both
call :docker_compose
call :kubernetes
exit /b 0
