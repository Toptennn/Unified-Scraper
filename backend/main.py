from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from scraper import DuckDuckGoScraper, TwitterScraper


from config import TwitterConfig, TwitterCredentials, SearchParameters, SearchMode
from scraper import TwitterScraper
from cookie_manager import RedisCookieManager
from data_utils import TweetDataExtractor

app = FastAPI(title="Unified Scraper API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequestDDG(BaseModel):
    normal_query: Optional[str] = ""
    exact_phrase: Optional[str] = ""
    semantic_query: Optional[str] = ""
    include_terms: Optional[str] = ""
    exclude_terms: Optional[str] = ""
    filetype: Optional[str] = ""
    site_include: Optional[str] = ""
    site_exclude: Optional[str] = ""
    intitle: Optional[str] = ""
    inurl: Optional[str] = ""
    max_pages: int = 20
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SearchResult(BaseModel):
    query: str
    pages_retrieved: int
    results: List[Dict]

class TimelineRequest(BaseModel):
    auth_id: str
    password: str
    screen_name: str
    count: int = 50


class SearchRequestX(BaseModel):
    auth_id: str
    password: str
    query: str
    count: int = 50
    mode: SearchMode = SearchMode.POPULAR
    start_date: Optional[str] = None
    end_date: Optional[str] = None


def _add_normal_query(queries, parts):
    if queries.get("normal_query"):
        parts.append(queries["normal_query"])

def _add_exact_phrase(queries, parts):
    if queries.get("exact_phrase"):
        parts.append(f'"{queries["exact_phrase"]}"')

def _add_semantic_query(queries, parts):
    if queries.get("semantic_query"):
        parts.append(f'~"{queries["semantic_query"]}"')

def _add_include_terms(queries, parts):
    if queries.get("include_terms"):
        terms = [t.strip() for t in queries["include_terms"].split(',') if t.strip()]
        parts.extend([f"+{t}" for t in terms])

def _add_exclude_terms(queries, parts):
    if queries.get("exclude_terms"):
        terms = [t.strip() for t in queries["exclude_terms"].split(',') if t.strip()]
        parts.extend([f"-{t}" for t in terms])

def _add_filetype(queries, parts):
    if queries.get("filetype"):
        parts.append(f"filetype:{queries['filetype']}")

def _add_site_include(queries, parts):
    if queries.get("site_include"):
        parts.append(f"site:{queries['site_include']}")

def _add_site_exclude(queries, parts):
    if queries.get("site_exclude"):
        parts.append(f"-site:{queries['site_exclude']}")

def _add_intitle(queries, parts):
    if queries.get("intitle"):
        parts.append(f"intitle:{queries['intitle']}")

def _add_inurl(queries, parts):
    if queries.get("inurl"):
        parts.append(f"inurl:{queries['inurl']}")

def build_query(queries: dict) -> str:
    parts = []
    _add_normal_query(queries, parts)
    _add_exact_phrase(queries, parts)
    _add_semantic_query(queries, parts)
    _add_include_terms(queries, parts)
    _add_exclude_terms(queries, parts)
    _add_filetype(queries, parts)
    _add_site_include(queries, parts)
    _add_site_exclude(queries, parts)
    _add_intitle(queries, parts)
    _add_inurl(queries, parts)
    return " ".join(parts)

@app.post("/ddg/search", response_model=SearchResult)
def search(req: SearchRequestDDG):
    queries = req.dict()
    max_pages = queries.pop("max_pages")
    start_date = queries.pop("start_date")
    end_date = queries.pop("end_date")
    final_query = build_query(queries)

    scraper = DuckDuckGoScraper()
    df, pages_retrieved = scraper.scrape(
        final_query,
        max_pages,
        headless=True,
        start_date=start_date,
        end_date=end_date,
    )
    results = df.to_dict(orient="records")
    return SearchResult(query=final_query, pages_retrieved=pages_retrieved, results=results)

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "DuckDuckGo Scraper API is running"}



async def create_scraper(auth_id: str, password: str) -> TwitterScraper:
    """Initialize scraper with credentials and authenticate."""
    cookie_manager = RedisCookieManager()
    cookie_path = cookie_manager.load_cookie(auth_id)
    credentials = TwitterCredentials(
        auth_id=auth_id,
        password=password,
        cookies_file=str(cookie_path)
    )
    config = TwitterConfig(credentials=credentials, output_dir="output")
    scraper = TwitterScraper(config, cookie_manager=cookie_manager)
    await scraper.authenticate()
    return scraper

@app.post("/X/timeline")
async def scrape_timeline(req: TimelineRequest):
    """Fetch tweets from a user's timeline."""
    scraper = await create_scraper(req.auth_id, req.password)
    user = await scraper.get_user_by_screen_name(req.screen_name)
    tweets = await scraper.fetch_user_timeline(user.id, count=req.count)
    return TweetDataExtractor.extract_tweet_data(tweets)


@app.post("/X/search")
async def search_tweets(req: SearchRequestX):
    """Search tweets based on query parameters."""
    scraper = await create_scraper(req.auth_id, req.password)
    params = SearchParameters(
        query=req.query,
        count=req.count,
        mode=req.mode,
        start_date=req.start_date,
        end_date=req.end_date,
    )
    tweets = await scraper.search_tweets(params)
    return TweetDataExtractor.extract_tweet_data(tweets)