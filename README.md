# Unified Scraper - DuckDuckGo & X (Twitter) Combined

A comprehensive web scraping solution that combines DuckDuckGo search and X (Twitter) data extraction capabilities into a single, unified web application.

## Features

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

## Technology Stack

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests
- **React Hooks**: State management and side effects

### Backend
- **FastAPI**: High-performance Python web framework
- **Pydantic**: Data validation and serialization
- **Selenium**: Web browser automation
- **TwiKit**: Twitter API interaction
- **Async/Await**: Asynchronous processing

### Data Processing
- **Pandas**: Data manipulation and analysis
- **BeautifulSoup**: HTML parsing
- **XLSX**: Excel file generation
- **Papa Parse**: CSV processing

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Chrome/Chromium browser (for DuckDuckGo scraping)

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Configuration
Create a `.env` file in the backend directory with your Twitter credentials and Redis configuration.

## Project Structure

```
unified-scraper/
├── frontend/                 # Next.js React application
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main layout wrapper
│   │   ├── Navigation.tsx   # Navigation header
│   │   ├── ThemeToggle.tsx  # Dark mode toggle
│   │   ├── SearchForm.tsx   # DuckDuckGo search form
│   │   ├── SearchResults.tsx # DuckDuckGo results display
│   │   ├── ResultsTable.tsx # DuckDuckGo results table
│   │   └── TweetTable.tsx   # Twitter results table
│   ├── pages/               # Next.js pages
│   │   ├── index.tsx        # Homepage
│   │   ├── duckduckgo.tsx   # DuckDuckGo scraper page
│   │   └── twitter.tsx      # Twitter scraper page
│   ├── types/               # TypeScript type definitions
│   └── styles/              # CSS styles
├── backend/                 # FastAPI Python backend
│   ├── main_unified.py      # Main API server
│   ├── requirements.txt     # Python dependencies
│   └── [scraper modules]    # Individual scraper implementations
└── README.md               # This file
```

## Usage

### DuckDuckGo Scraper
1. Navigate to `/ddg`
2. Enter search parameters (normal query, exact phrase, etc.)
3. Configure advanced options (file types, site filters, date ranges)
4. Click "Search DuckDuckGo" to start scraping
5. View results in the interactive table
6. Export data as CSV or Excel

### X (Twitter) Scraper
1. Navigate to `/X`
2. Enter your Twitter credentials
3. Choose scraping mode (timeline, latest, popular)
4. Configure search parameters or username
5. Set the number of tweets to retrieve
6. Click "Start Scraping"
7. Filter results by username or keywords
8. Export data as CSV or Excel

## API Endpoints

### DuckDuckGo
- `POST /ddg/search` - Advanced DuckDuckGo search

### Twitter
- `POST /X/timeline` - Get user timeline
- `POST /X/search` - Search tweets

### Health
- `GET /` - API status
- `GET /health` - Health check

## Features in Detail

### Advanced Search Options (DuckDuckGo)
- **Semantic Search**: Use semantic operators for better relevance
- **Site Filtering**: Include or exclude specific domains
- **File Type Restrictions**: Search for specific file types (PDF, DOC, etc.)
- **Date Range Filtering**: Limit results to specific time periods
- **Title/URL Search**: Search within page titles or URLs

### Twitter Data Extraction
- **Timeline Scraping**: Extract tweets from specific user timelines
- **Search Functionality**: Find tweets matching specific criteria
- **Engagement Metrics**: Retweet, like, and reply counts
- **Date Filtering**: Search within specific date ranges
- **Export Options**: Multiple format support for data export

### User Experience
- **Real-time Updates**: Live feedback during scraping operations
- **Progress Indicators**: Visual progress bars and loading states
- **Error Handling**: Comprehensive error messages and recovery
- **Responsive Design**: Optimized for all device sizes
- **Accessibility**: WCAG compliant interface elements

## Development

### Running in Development Mode
```bash
# Terminal 1 - Frontend
cd frontend
npm run dev

# Terminal 2 - Backend
cd backend
uvicorn main:app --reload
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of service of the platforms being scraped.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with the terms of service of DuckDuckGo, Twitter/X, and any other platforms they interact with. The developers are not responsible for any misuse of this tool.

## Support

For issues, questions, or contributions, please open an issue on the project repository.
