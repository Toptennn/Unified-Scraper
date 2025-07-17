# Docker Deployment Guide

This guide will help you deploy the Unified Scraper application using Docker Hub images.

## Prerequisites

- Docker Desktop installed and running
- Docker Hub account (for pushing images)

## Available Images

The following images are available on Docker Hub:

- `topten10/unified-scraper-backend:latest` - Backend API service
- `topten10/unified-scraper-frontend:latest` - Frontend Next.js application

## Quick Start

### 1. Pull and Run with Docker Compose (Recommended)

```bash
# Clone the repository (if not already done)
git clone https://github.com/Toptennn/Unified-Scraper.git
cd Unified-Scraper

# Create environment file for backend
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration

# Run using production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Manual Docker Run

```bash
# Run backend
docker run -d \
  --name scraper-backend \
  --env-file ./backend/.env \
  -e DOCKER_CONTAINER=true \
  -p 8000:8000 \
  topten10/unified-scraper-backend:latest

# Run frontend
docker run -d \
  --name scraper-frontend \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -p 3000:3000 \
  topten10/unified-scraper-frontend:latest
```

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Redis Configuration (Required)
UPSTASH_REDIS_REST_URL=your_redis_url_here
UPSTASH_REDIS_REST_TOKEN=your_redis_token_here

# Optional: Rate limiting settings
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Docker flag (automatically set in containers)
DOCKER_CONTAINER=true
```

### Frontend Environment Variables

The frontend uses the following environment variable:

- `NEXT_PUBLIC_API_URL`: URL of the backend API (default: http://localhost:8000)

## Features

- **DuckDuckGo Scraping**: Advanced search with multiple query parameters
- **Twitter/X Scraping**: Timeline and search functionality
- **Real-time Updates**: Streaming results with progress tracking
- **Modern UI**: React-based frontend with responsive design
- **Cookie Management**: Redis-based session management

## API Endpoints

### DuckDuckGo
- `POST /ddg/search` - Search with parameters
- `GET /ddg/search-stream` - Streaming search results

### Twitter/X
- `POST /X/search` - Search tweets
- `POST /X/timeline` - Get user timeline
- `GET /X/search-stream` - Streaming tweet search
- `GET /X/timeline-stream` - Streaming timeline

## Environment Variables

### Backend
- `UPSTASH_REDIS_REST_URL` - Redis connection URL
- `UPSTASH_REDIS_REST_TOKEN` - Redis authentication token
- `DOCKER_CONTAINER` - Set to "true" for container deployment

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Docker Images

- **Backend**: `yourusername/unified-scraper-backend:latest`
- **Frontend**: `yourusername/unified-scraper-frontend:latest`

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │────│   Backend   │────│    Redis    │
│  (Next.js)  │    │  (FastAPI)  │    │ (Cookies)   │
│   Port 3000 │    │  Port 8000  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Development

For development setup, see the main repository README.

## License

MIT License
