# Unified Scraper - DuckDuckGo & X (Twitter) Combined

A comprehensive, production-ready web scraping solution that combines DuckDuckGo search and X (Twitter) data extraction capabilities into a single, unified web application with modern UI/UX design.

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
