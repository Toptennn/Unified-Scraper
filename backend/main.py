from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from scraper import DuckDuckGoScraper, TwitterScraper
import uuid
import asyncio

from config import TwitterConfig, TwitterCredentials, SearchParameters, SearchMode
from scraper import TwitterScraper
from cookie_manager import RedisCookieManager
from data_utils import TweetDataExtractor
from auth_handler import InteractiveAuthHandler, AuthSessionManager, VerificationChallenge

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


# New request models for authenticated users (no password required)
class AuthenticatedTimelineRequest(BaseModel):
    auth_id: str
    screen_name: str
    count: int = 50


class AuthenticatedSearchRequest(BaseModel):
    auth_id: str
    query: str
    count: int = 50
    mode: SearchMode = SearchMode.POPULAR
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# New models for authentication challenge flow
class AuthRequest(BaseModel):
    auth_id: str
    password: str


class AuthChallenge(BaseModel):
    session_id: str
    challenge_type: str  # "email_verification" or "confirmation_code"
    message: str
    hint: Optional[str] = None


class AuthChallengeResponse(BaseModel):
    session_id: str
    response: str


class AuthResult(BaseModel):
    success: bool
    session_id: Optional[str] = None
    challenge: Optional[AuthChallenge] = None
    message: str


# Global storage for authentication sessions (in production, use Redis or database)
auth_sessions: Dict[str, Dict[str, Any]] = {}

# Initialize session manager
session_manager = AuthSessionManager()
auth_handler = InteractiveAuthHandler(session_manager)


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


# ==================== Authentication Endpoints ====================

@app.post("/X/auth/start", response_model=AuthResult)
async def start_authentication(req: AuthRequest):
    """Start Twitter authentication process."""
    try:
        session_id = str(uuid.uuid4())
        cookie_manager = RedisCookieManager()
        cookie_path = cookie_manager.load_cookie(req.auth_id)
        
        # Attempt authentication
        await auth_handler.authenticate_with_challenge_support(
            session_id, req.auth_id, req.password, str(cookie_path)
        )
        
        # If we reach here, authentication was successful
        # Save cookies and cleanup session
        cookie_manager.save_cookie(req.auth_id, cleanup=True)
        session_manager.cleanup_session(session_id)
        
        return AuthResult(
            success=True,
            message="Authentication successful"
        )
        
    except VerificationChallenge as e:
        # Return challenge to frontend
        challenge = AuthChallenge(
            session_id=session_id,
            challenge_type=e.challenge_type,
            message=e.message,
            hint=e.hint
        )
        
        return AuthResult(
            success=False,
            session_id=session_id,
            challenge=challenge,
            message="Verification required"
        )
        
    except Exception as e:
        return AuthResult(
            success=False,
            message=f"Authentication failed: {str(e)}"
        )


@app.post("/X/auth/verify", response_model=AuthResult)
async def verify_challenge(req: AuthChallengeResponse):
    """Submit verification challenge response."""
    try:
        session = session_manager.get_session(req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Invalid session ID")
        
        # Continue authentication with verification response
        await auth_handler.continue_authentication(req.session_id, req.response)
        
        # If we reach here, authentication was successful
        cookie_manager = RedisCookieManager()
        cookie_manager.save_cookie(session['auth_id'], cleanup=True)
        session_manager.cleanup_session(req.session_id)
        
        return AuthResult(
            success=True,
            message="Authentication successful"
        )
        
    except VerificationChallenge as e:
        # Another challenge is needed
        challenge = AuthChallenge(
            session_id=req.session_id,
            challenge_type=e.challenge_type,
            message=e.message,
            hint=e.hint
        )
        
        return AuthResult(
            success=False,
            session_id=req.session_id,
            challenge=challenge,
            message="Additional verification required"
        )
        
    except Exception as e:
        session_manager.cleanup_session(req.session_id)
        return AuthResult(
            success=False,
            message=f"Verification failed: {str(e)}"
        )


@app.get("/")
def health_check():
    return {"status": "healthy", "message": "Unified Scraper API is running"}


# ==================== Twitter Scraping Endpoints ====================



async def create_scraper(auth_id: str, password: str) -> TwitterScraper:
    """Initialize scraper with credentials and authenticate."""
    cookie_manager = RedisCookieManager()
    cookie_path = cookie_manager.load_cookie(auth_id)
    first_login = not cookie_path.exists()
    credentials = TwitterCredentials(
        auth_id=auth_id,
        password=password,
        cookies_file=str(cookie_path)
    )
    config = TwitterConfig(credentials=credentials, output_dir="output")
    scraper = TwitterScraper(config, cookie_manager=cookie_manager)
    await scraper.authenticate(cleanup_cookie=first_login)
    return scraper


async def create_authenticated_scraper(auth_id: str) -> TwitterScraper:
    """Create scraper for already authenticated user."""
    cookie_manager = RedisCookieManager()
    cookie_path = cookie_manager.load_cookie(auth_id)
    
    if not cookie_path.exists():
        raise HTTPException(
            status_code=401, 
            detail="No valid authentication found. Please authenticate first using /X/auth/start"
        )
    
    credentials = TwitterCredentials(
        auth_id=auth_id,
        password="",  # Not needed for cookie-based auth
        cookies_file=str(cookie_path)
    )
    config = TwitterConfig(credentials=credentials, output_dir="output")
    scraper = TwitterScraper(config, cookie_manager=cookie_manager)
    
    # Try to use existing cookies without re-authentication
    try:
        await scraper.client.login(
            auth_info_1=auth_id,
            password="",
            cookies_file=str(cookie_path)
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Authentication expired. Please re-authenticate using /X/auth/start"
        )
    
    return scraper

@app.post("/X/timeline")
async def scrape_timeline(req: TimelineRequest):
    """Fetch tweets from a user's timeline (legacy endpoint with password)."""
    scraper = await create_scraper(req.auth_id, req.password)
    user = await scraper.get_user_by_screen_name(req.screen_name)
    tweets = await scraper.fetch_user_timeline(user.id, count=req.count)
    return TweetDataExtractor.extract_tweet_data(tweets)


@app.post("/X/search")
async def search_tweets(req: SearchRequestX):
    """Search tweets based on query parameters (legacy endpoint with password)."""
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


# New authenticated endpoints (recommended)
@app.post("/X/timeline/authenticated")
async def scrape_timeline_authenticated(req: AuthenticatedTimelineRequest):
    """Fetch tweets from a user's timeline (requires prior authentication)."""
    scraper = await create_authenticated_scraper(req.auth_id)
    user = await scraper.get_user_by_screen_name(req.screen_name)
    tweets = await scraper.fetch_user_timeline(user.id, count=req.count)
    return TweetDataExtractor.extract_tweet_data(tweets)


@app.post("/X/search/authenticated")
async def search_tweets_authenticated(req: AuthenticatedSearchRequest):
    """Search tweets based on query parameters (requires prior authentication)."""
    scraper = await create_authenticated_scraper(req.auth_id)
    params = SearchParameters(
        query=req.query,
        count=req.count,
        mode=req.mode,
        start_date=req.start_date,
        end_date=req.end_date,
    )
    tweets = await scraper.search_tweets(params)
    return TweetDataExtractor.extract_tweet_data(tweets)