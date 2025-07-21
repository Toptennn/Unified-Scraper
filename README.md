# Unified Scraper - DuckDuckGo & X (Twitter) Combined

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

A comprehensive, production-ready web scraping solution that combines DuckDuckGo search and X (Twitter) data extraction capabilities into a single, unified web application with modern UI/UX design.

## 📑 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Features in Detail](#features-in-detail)
- [Development](#development)
- [Docker Support](#docker-support)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Features

### DuckDuckGo Scraper
- **Advanced Search Parameters**: Normal query, exact phrase, semantic search
- **Filter Options**: Include/exclude terms, file types, site restrictions
- **Special Operators**: intitle, inurl search operators
- **Date Filtering**: Search within specific date ranges
- **Export Capabilities**: CSV and Excel export functionality
- **Real-time Results**: Live search results with pagination

### X (Twitter) Scraper
- **Multiple Modes**: User timeline, latest tweets, popular tweets
- **Advanced Search**: Keyword-based search with date filtering
- **Data Export**: CSV and Excel export with comprehensive tweet data
- **Real-time Filtering**: Filter results by username and keywords
- **Rich Data**: Tweet metadata including engagement metrics

### Unified Features
- **Single Interface**: Access both scrapers from one application
- **Consistent UI**: Unified design system across all pages
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Navigation**: Easy switching between different scraper tools
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Recovery**: Automatic retry mechanisms and error handling

## 🛠 Technology Stack

### Frontend
- **Next.js 14**: React framework with App Router and server-side rendering
- **TypeScript**: Type-safe development with enhanced IDE support
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Axios**: HTTP client for API requests with interceptors
- **React Hooks**: Modern state management and side effects
- **Papa Parse**: Efficient CSV parsing and generation

### Backend
- **FastAPI**: High-performance Python web framework with auto-generated docs
- **Pydantic**: Data validation and serialization with type hints
- **Selenium**: Web browser automation for dynamic content scraping
- **TwiKit**: Modern Twitter API interaction library
- **Async/Await**: Asynchronous processing for better performance
- **CORS**: Cross-Origin Resource Sharing support

### Data Processing & Storage
- **Pandas**: Advanced data manipulation and analysis
- **BeautifulSoup4**: HTML parsing and extraction
- **OpenPyXL**: Excel file generation and manipulation
- **JSON**: Structured data serialization
- **File System**: Local storage for cookies and cache

### Development & Deployment
- **Docker**: Containerization for both frontend and backend
- **uvicorn**: ASGI server for production deployment
- **Node.js**: JavaScript runtime for frontend development
- **npm**: Package management for frontend dependencies

## ⚡ Installation & Setup

### Prerequisites
- **Node.js**: Version 18+ with npm (for frontend)
- **Python**: Version 3.8+ with pip (for backend)
- **Chrome/Chromium**: Browser for DuckDuckGo scraping automation
- **Git**: Version control system

### Quick Start

#### 1. Clone the Repository
```bash
git clone https://github.com/Toptennn/Unified-Scraper.git
cd unified-scraper
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: http://localhost:3000

#### 3. Backend Setup
```bash
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend API will be available at: http://localhost:8000

#### 4. Environment Configuration
Create a `.env` file in the `backend` directory:
```env
# Twitter/X Credentials (optional - for Twitter scraping)
TWITTER_USERNAME=your_username
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_password

# Optional: Rate limiting and performance settings
MAX_WORKERS=5
REQUEST_TIMEOUT=30
```

### Alternative: Docker Setup
```bash
# Build and run both services
docker-compose up --build

# Or run individually
docker build -t unified-scraper-frontend ./frontend
docker build -t unified-scraper-backend ./backend
```

## 📁 Project Structure

```
unified-scraper/
├── 📁 frontend/                    # Next.js React application
│   ├── 📁 components/             # Reusable UI components
│   │   ├── Layout.tsx            # Main layout wrapper with navigation
│   │   ├── Navigation.tsx        # Header navigation component
│   │   ├── ThemeToggle.tsx       # Dark/light mode toggle
│   │   ├── SearchForm.tsx        # DuckDuckGo search form
│   │   ├── SearchResults.tsx     # DuckDuckGo results display
│   │   ├── ResultsTable.tsx      # DuckDuckGo results table
│   │   ├── TweetTable.tsx        # Twitter results table
│   │   └── ProgressBar.tsx       # Loading progress indicator
│   ├── 📁 pages/                 # Next.js pages and routing
│   │   ├── _app.tsx             # App wrapper with providers
│   │   ├── index.tsx            # Homepage and landing page
│   │   ├── duckduckgo.tsx       # DuckDuckGo scraper interface
│   │   └── twitter.tsx          # Twitter scraper interface
│   ├── 📁 types/                # TypeScript type definitions
│   │   └── index.ts             # Shared type interfaces
│   ├── 📁 styles/               # CSS and styling
│   │   └── globals.css          # Global styles and Tailwind
│   ├── 📁 hooks/                # Custom React hooks
│   ├── package.json             # Dependencies and scripts
│   ├── tsconfig.json            # TypeScript configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   ├── next.config.js           # Next.js configuration
│   └── Dockerfile               # Docker container config
├── 📁 backend/                    # FastAPI Python backend
│   ├── main.py                  # Main API server and endpoints
│   ├── config.py                # Application configuration
│   ├── 📁 scraper/              # Scraping modules
│   │   ├── __init__.py          # Package initialization
│   │   ├── duckduckgo.py        # DuckDuckGo scraper logic
│   │   └── X.py                 # Twitter/X scraper logic
│   ├── cookie_manager.py        # Cookie handling and persistence
│   ├── data_utils.py            # Data processing utilities
│   ├── query_builder.py         # Search query construction
│   ├── rate_limiter.py          # Request rate limiting
│   ├── test_chrome.py           # Chrome setup testing
│   ├── requirements.txt         # Python dependencies
│   ├── 📁 cookies/              # Cookie storage directory
│   ├── 📁 output/               # Generated files output
│   ├── .env                     # Environment variables
│   └── Dockerfile               # Docker container config
├── README.md                     # Project documentation
└── docker-compose.yml           # Multi-container Docker setup
```

## 📖 Usage

### DuckDuckGo Scraper
1. **Navigate** to `/duckduckgo` in the application
2. **Enter Search Parameters**:
   - Normal query terms
   - Exact phrase (in quotes)
   - Include/exclude specific terms
3. **Configure Advanced Options**:
   - File types (PDF, DOC, PPT, etc.)
   - Site filters (include/exclude domains)
   - Date ranges for temporal filtering
   - Special operators (intitle:, inurl:)
4. **Execute Search**: Click "Search DuckDuckGo" to start scraping
5. **View Results**: Browse results in the interactive data table
6. **Export Data**: Download as CSV or Excel format
7. **Refine Search**: Modify parameters and re-run as needed

### X (Twitter) Scraper
1. **Navigate** to `/twitter` in the application
2. **Authentication Setup**:
   - **Auth ID/Username**: Your Twitter username or phone number
   - **Email Address**: Your Twitter account email address  
   - **Password**: Your Twitter password
   
   > ⚠️ **Security Note**: Credentials are used only for session authentication and are not stored permanently.

3. **Choose Scraping Mode**:
   - **User Timeline**: Get tweets from a specific user
   - **Latest Tweets**: Search for recent tweets by keyword
   - **Popular Tweets**: Find trending tweets by keyword

4. **Configure Parameters**:
   - Username (for timeline mode)
   - Search keywords (for search modes)
   - Number of tweets to retrieve (1-1000)
   - Date range filtering (optional)

5. **Start Scraping**: Click "Start Scraping" and monitor progress
6. **Filter Results**: Use real-time filters for username/keywords
7. **Export Data**: Download comprehensive tweet data as CSV/Excel

### Navigation Tips
- Use the **navigation bar** to switch between tools seamlessly
- Toggle **dark/light mode** for comfortable viewing
- All forms include **real-time validation** and helpful tooltips
- **Progress bars** show scraping status and completion

## 🔌 API Endpoints

### DuckDuckGo Endpoints
- **`POST /ddg/search`** - Advanced DuckDuckGo search
  ```json
  {
    "normal_query": "machine learning",
    "exact_phrase": "artificial intelligence",
    "include_terms": ["python", "tensorflow"],
    "exclude_terms": ["java"],
    "site_filter": "github.com",
    "file_type": "pdf",
    "date_range": "week"
  }
  ```

### Twitter/X Endpoints
- **`POST /X/timeline`** - Get user timeline tweets
  ```json
  {
    "username": "elonmusk",
    "count": 50,
    "auth": {
      "username": "your_username",
      "email": "your_email",
      "password": "your_password"
    }
  }
  ```

- **`POST /X/search`** - Search tweets by keywords
  ```json
  {
    "query": "artificial intelligence",
    "count": 100,
    "search_type": "latest",
    "auth": {
      "username": "your_username",
      "email": "your_email", 
      "password": "your_password"
    }
  }
  ```

### Health & Status
- **`GET /`** - API status and welcome message
- **`GET /health`** - Detailed health check with system info
- **`GET /docs`** - Interactive API documentation (Swagger UI)
- **`GET /redoc`** - Alternative API documentation (ReDoc)

### Response Format
All endpoints return standardized JSON responses:
```json
{
  "status": "success|error",
  "data": [...],
  "message": "Operation completed successfully",
  "total_results": 42,
  "processing_time": "2.3s"
}
```

## 🎯 Features in Detail

### Advanced Search Options (DuckDuckGo)
- **Semantic Search**: Leverage advanced search operators for precise results
- **Boolean Logic**: Combine AND, OR, NOT operations for complex queries
- **Site Filtering**: Include (`site:example.com`) or exclude (`-site:spam.com`) specific domains
- **File Type Restrictions**: Target specific formats (PDF, DOC, PPT, XLS, etc.)
- **Date Range Filtering**: Limit results to specific time periods (day, week, month, year)
- **Title/URL Search**: Search within page titles (`intitle:`) or URLs (`inurl:`)
- **Content Type Filtering**: Images, videos, news, or web results
- **Language Detection**: Filter by content language
- **Safe Search**: Content filtering options

### Twitter Data Extraction
- **Timeline Scraping**: Extract complete user timelines with historical data
- **Advanced Search**: Multi-keyword search with boolean operators
- **Engagement Metrics**: Comprehensive data including:
  - Retweet counts and retweet data
  - Like/favorite counts
  - Reply counts and reply threads
  - Quote tweet information
  - View counts (when available)
- **Temporal Filtering**: Date range searches with precision
- **Export Formats**: CSV, Excel, JSON with customizable field selection
- **Media Detection**: Identify tweets with images, videos, or links
- **Thread Reconstruction**: Maintain tweet thread relationships

### User Experience Excellence
- **Real-time Updates**: Live progress tracking with WebSocket connections
- **Progress Indicators**: Visual progress bars with ETA calculations
- **Intelligent Error Handling**: 
  - Automatic retry mechanisms
  - Graceful degradation
  - User-friendly error messages
  - Recovery suggestions
- **Responsive Design**: 
  - Mobile-optimized interface
  - Tablet-friendly layouts
  - Desktop power-user features
- **Accessibility Features**:
  - WCAG 2.1 AA compliance
  - Keyboard navigation support
  - Screen reader compatibility
  - High contrast mode support
- **Performance Optimization**:
  - Lazy loading for large datasets
  - Client-side caching
  - Optimistic updates
  - Background processing

### Data Management
- **Export Options**: Multiple format support (CSV, Excel, JSON)
- **Data Validation**: Real-time validation with error highlighting
- **Batch Processing**: Handle large datasets efficiently
- **Resume Capability**: Resume interrupted scraping sessions
- **Data Deduplication**: Automatic duplicate detection and removal
- **Filtering & Sorting**: Advanced client-side data manipulation
- **Search Integration**: Full-text search within results

## 👨‍💻 Development

### Running in Development Mode
```bash
# Terminal 1 - Frontend with hot reload
cd frontend
npm run dev
# Runs on http://localhost:3000

# Terminal 2 - Backend with auto-reload
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Runs on http://localhost:8000
```

### Building for Production
```bash
# Frontend production build
cd frontend
npm run build
npm start

# Backend production setup
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Development Tools & Scripts
```bash
# Frontend
npm run lint          # ESLint code linting
npm run type-check     # TypeScript type checking
npm run build         # Production build
npm run start         # Production server

# Backend
python -m pytest     # Run test suite
python -m black .     # Code formatting
python -m flake8      # PEP 8 style checking
```

### Code Style & Standards
- **Frontend**: ESLint + Prettier for JavaScript/TypeScript
- **Backend**: Black + Flake8 for Python PEP 8 compliance
- **Git**: Conventional commits with semantic versioning
- **Documentation**: JSDoc for frontend, docstrings for backend

## 🐳 Docker Support

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Individual Docker Containers
```bash
# Frontend container
docker build -t unified-scraper-frontend ./frontend
docker run -p 3000:3000 unified-scraper-frontend

# Backend container
docker build -t unified-scraper-backend ./backend
docker run -p 8000:8000 unified-scraper-backend
```

### Production Docker Configuration
```yaml
# docker-compose.prod.yml example
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:3000"
    environment:
      - NODE_ENV=production
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    volumes:
      - ./data:/app/data
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Frontend Issues
**Problem**: `npm install` fails with dependency conflicts
```bash
# Solution: Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem**: TypeScript compilation errors
```bash
# Solution: Check TypeScript configuration
npm run type-check
# Fix any type errors shown
```

#### Backend Issues
**Problem**: ChromeDriver not found for DuckDuckGo scraping
```bash
# Solution: Install ChromeDriver manually
# Windows:
choco install chromedriver
# macOS:
brew install chromedriver
# Linux:
sudo apt-get install chromium-chromedriver
```

**Problem**: Twitter authentication fails
```bash
# Solution: Verify credentials in .env file
# Check for 2FA enabled accounts (not currently supported)
# Ensure account is not locked or suspended
```

**Problem**: Rate limiting errors
```bash
# Solution: Adjust rate limiting in config.py
# Increase delays between requests
# Use proxy rotation if needed
```

#### General Issues
**Problem**: CORS errors in development
```bash
# Solution: Check CORS settings in main.py
# Ensure frontend URL is in allowed origins
```

**Problem**: High memory usage during scraping
```bash
# Solution: Reduce batch size in scraper configuration
# Implement pagination for large datasets
# Monitor system resources
```

### Performance Optimization
- **Frontend**: Enable production build optimizations
- **Backend**: Use async/await for concurrent operations
- **Database**: Implement connection pooling if using databases
- **Caching**: Enable Redis for session management
- **Monitoring**: Use logging for performance tracking

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test` (frontend) and `pytest` (backend)
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation for any API changes
- Ensure all tests pass before submitting PR
- Keep commits atomic and well-described

### Code Review Process
1. All PRs require at least one review
2. Automated tests must pass
3. Code style checks must pass
4. Documentation must be updated if needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Selenium](https://selenium.dev/) - Browser automation
- [TwiKit](https://github.com/d60/twikit) - Twitter API library

## 📊 Project Status

- ✅ **Core Features**: Implemented and tested
- ✅ **UI/UX**: Modern, responsive design
- ✅ **Docker Support**: Production-ready containers
- 🚧 **Advanced Analytics**: In development
- 🚧 **API Rate Limiting**: Enhanced implementation in progress
- 📋 **Proxy Support**: Planned for next release

---

**Built with ❤️ by the Unified Scraper Team**

For questions, issues, or feature requests, please visit our [GitHub Issues](https://github.com/Toptennn/Unified-Scraper/issues) page.
