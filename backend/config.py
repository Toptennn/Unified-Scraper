"""
Configuration classes and enums for the X/Twitter scraper.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pathlib import Path


# ---------------------------------------------------------------------------
# DuckDuckGo Scraper Configuration
# ---------------------------------------------------------------------------

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Enhanced Chrome options for maximum stability in cloud environments
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-setuid-sandbox', 
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess',
    '--disable-ipc-flooding-protection',
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-default-apps',
    '--no-default-browser-check',
    '--disable-hang-monitor',
    '--disable-prompt-on-repost',
    '--disable-sync',
    '--disable-background-networking',
    '--disable-infobars',
    '--disable-notifications',
    '--disable-logging',
    '--disable-gpu-logging',
    '--silent',
    '--log-level=3',
    '--window-size=1280,720',
    '--remote-debugging-port=0',
    '--disable-client-side-phishing-detection',
    '--disable-crash-reporter',
    '--disable-oopr-debug-crash-dump',
    '--no-crash-upload',
    '--disable-low-res-tiling',
    '--memory-pressure-off',
    '--disable-permissions-api',
    '--disable-component-update',
    '--disable-domain-reliability',
    '--aggressive-cache-discard',
    '--disable-file-system',
    '--disable-databases',
    '--disable-local-storage'
]

# Add cloud-specific options
if os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD'):
    CHROME_OPTIONS.extend([
        '--single-process',
        '--no-zygote',
        '--disable-gpu-sandbox',
        '--disable-software-rasterizer',
        '--disable-dev-shm-usage',
        '--memory-pressure-off',
        '--max_old_space_size=2048',  # Reduced memory
        '--js-flags="--max-old-space-size=2048"',
        '--disable-background-timer-throttling',
        '--disable-renderer-backgrounding',
        '--disable-backgrounding-occluded-windows'
    ])

# Enhanced result selectors for better compatibility
RESULT_SELECTORS = [
    "article[data-testid='result']",
    "article[data-nrn='result']", 
    ".result",
    "[data-testid='result']",
    ".web-result",
    ".result__body",
    "div[data-area='primary'] > div > div",
    "#links .result",
    ".organic-result",
    ".results_links",
    ".result--default"
]

# Enhanced link selectors
LINK_SELECTORS = [
    "a[data-testid='result-title-a']",
    "h2 a",
    "h3 a", 
    ".result__title a",
    ".result-title a",
    ".result__url",
    "a[href*='http']"
]

# Enhanced more results selectors
MORE_RESULTS_SELECTORS = [
    "button#more-results",
    "button[id='more-results']",
    ".more-results",
    "button:contains('More results')",
    "a:contains('More results')",
    ".more_results",
    "[data-testid='more-results']"
]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SearchType(Enum):
    """Which tab to hit when searching tweets."""
    TOP = "Top"
    LATEST = "Latest"


class SearchMode(Enum):
    """High-level search modes exposed to the user."""
    DATE_RANGE = "date_range"
    POPULAR    = "popular"
    LATEST     = "latest"


# ---------------------------------------------------------------------------
# Low-level configs
# ---------------------------------------------------------------------------

@dataclass
class RateLimitConfig:
    """Back-off strategy when the scraper is rate-limited."""
    max_retries: int   = 3
    base_delay: float  = 1.0
    max_delay: float   = 300.0          # ≤ 5 min
    backoff_multiplier: float = 2.0
    jitter: bool       = True
    respect_reset_time: bool = True


@dataclass
class TwitterCredentials:
    """Login / cookie information."""
    auth_id: str
    password: str
    # Path to this user’s cookie file; None ➜ login each time
    cookies_file: Optional[str] = None


# ---------------------------------------------------------------------------
# User-facing params
# ---------------------------------------------------------------------------

@dataclass
class SearchParameters:
    """Parameters for a single tweet search."""
    query: str
    count: int                    = 100
    mode: SearchMode              = SearchMode.POPULAR
    start_date: Optional[str]     = None
    end_date: Optional[str]       = None

    def __post_init__(self):
        if self.mode is SearchMode.DATE_RANGE and (not self.start_date or not self.end_date):
            raise ValueError("Date-range search requires both start_date and end_date.")


# ---------------------------------------------------------------------------
# Top-level config that gets passed around
# ---------------------------------------------------------------------------

@dataclass
class TwitterConfig:
    credentials: TwitterCredentials
    output_dir: str                       = "output"
    search_params: Optional[SearchParameters] = None

    @classmethod
    def create_default(cls) -> "TwitterConfig":
        """Blank config stub – fill in credentials later."""
        return cls(
            credentials=TwitterCredentials(auth_id="", password="", cookies_file=None)
        )


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# Central place for every module to know where cookie files live
COOKIES_DIR = Path("cookies")
COOKIES_DIR.mkdir(exist_ok=True)
