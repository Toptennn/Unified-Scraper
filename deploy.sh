#!/bin/bash
# Deployment script for Unified Scraper (Linux/macOS)

echo "🚀 Unified Scraper Deployment Script"
echo "====================================="
echo ""

# Check if Docker is running
echo "Checking Docker status..."
if docker version > /dev/null 2>&1; then
    echo "✅ Docker is running"
else
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

# Login to Docker Hub
echo ""
echo "Logging into Docker Hub..."
docker login

if [ $? -ne 0 ]; then
    echo "❌ Docker login failed"
    exit 1
fi

# Build and push backend image
echo ""
echo "🔨 Building backend image..."
cd ./backend
docker build -t topten10/unified-scraper-backend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Backend image built successfully"
    echo "📤 Pushing backend image to Docker Hub..."
    docker push topten10/unified-scraper-backend:latest
    
    if [ $? -eq 0 ]; then
        echo "✅ Backend image pushed successfully"
    else
        echo "❌ Failed to push backend image"
    fi
else
    echo "❌ Failed to build backend image"
fi

# Build and push frontend image
echo ""
echo "🔨 Building frontend image..."
cd ../frontend
docker build -t topten10/unified-scraper-frontend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Frontend image built successfully"
    echo "📤 Pushing frontend image to Docker Hub..."
    docker push topten10/unified-scraper-frontend:latest
    
    if [ $? -eq 0 ]; then
        echo "✅ Frontend image pushed successfully"
    else
        echo "❌ Failed to push frontend image"
    fi
else
    echo "❌ Failed to build frontend image"
fi

# Return to root directory
cd ..

echo ""
echo "🎉 Deployment completed!"
echo "Your images are now available on Docker Hub:"
echo "- topten10/unified-scraper-backend:latest"
echo "- topten10/unified-scraper-frontend:latest"
echo ""
echo "To deploy using production compose file:"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "To check deployment status:"
echo "docker-compose -f docker-compose.prod.yml ps"
