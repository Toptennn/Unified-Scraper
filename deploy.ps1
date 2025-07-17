#!/usr/bin/env pwsh
# Deployment script for Unified Scraper

Write-Host "🚀 Unified Scraper Deployment Script" -ForegroundColor Green
Write-Host "=====================================`n" -ForegroundColor Green

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Login to Docker Hub
Write-Host "`nLogging into Docker Hub..." -ForegroundColor Yellow
docker login

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker login failed" -ForegroundColor Red
    exit 1
}

# Build and push backend image
Write-Host "`n🔨 Building backend image..." -ForegroundColor Yellow
Set-Location "./backend"
docker build -t topten10/unified-scraper-backend:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend image built successfully" -ForegroundColor Green
    Write-Host "📤 Pushing backend image to Docker Hub..." -ForegroundColor Yellow
    docker push topten10/unified-scraper-backend:latest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend image pushed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to push backend image" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to build backend image" -ForegroundColor Red
}

# Build and push frontend image
Write-Host "`n🔨 Building frontend image..." -ForegroundColor Yellow
Set-Location "../frontend"
docker build -t topten10/unified-scraper-frontend:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend image built successfully" -ForegroundColor Green
    Write-Host "📤 Pushing frontend image to Docker Hub..." -ForegroundColor Yellow
    docker push topten10/unified-scraper-frontend:latest
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend image pushed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to push frontend image" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to build frontend image" -ForegroundColor Red
}

# Return to root directory
Set-Location ".."

Write-Host "`n🎉 Deployment completed!" -ForegroundColor Green
Write-Host "Your images are now available on Docker Hub:" -ForegroundColor Cyan
Write-Host "- topten10/unified-scraper-backend:latest" -ForegroundColor White
Write-Host "- topten10/unified-scraper-frontend:latest" -ForegroundColor White

Write-Host "`nTo deploy using production compose file:" -ForegroundColor Cyan
Write-Host "docker-compose -f docker-compose.prod.yml up -d" -ForegroundColor White

Write-Host "`nTo check deployment status:" -ForegroundColor Cyan
Write-Host "docker-compose -f docker-compose.prod.yml ps" -ForegroundColor White
