import datetime
import os
from urllib.parse import quote_plus
import time
import re

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import config

class DuckDuckGoScraper:
    """DuckDuckGo search results scraper using Selenium."""

    def __init__(self):
        # This constructor is intentionally left empty because
        # all configuration and setup are handled in other methods.
        pass

    def _setup_driver(self, headless: bool = True):
        """Setup and configure Chrome driver with performance optimizations."""
        chrome_options = Options()
        
        # Basic Chrome options
        for option in config.CHROME_OPTIONS:
            chrome_options.add_argument(option)
        
        # Force headless in Docker environments or when requested
        if (headless or 
            os.path.exists('/.dockerenv') or  # Docker detection
            os.getenv('DOCKER_CONTAINER')):   # Docker environment variable
            chrome_options.add_argument('--headless=new')
        
        # Docker-specific Chrome options
        if os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER'):
            docker_options = [
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI,VizDisplayCompositor',
                '--disable-ipc-flooding-protection',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--run-all-compositor-stages-before-draw',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-hang-monitor',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--enable-automation',
                '--password-store=basic',
                '--use-mock-keychain',
                '--single-process',
                '--disable-blink-features=AutomationControlled',
                '--window-size=1920,1080',
                '--start-maximized'
            ]
            for option in docker_options:
                chrome_options.add_argument(option)
        
        # Performance-focused options
        performance_options = [
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--disable-sync',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--memory-pressure-off',
            '--max_old_space_size=4096',
            '--aggressive-cache-discard',
            '--disable-background-networking',
            '--disable-component-update',
            '--disable-domain-reliability'
        ]
        
        for option in performance_options:
            chrome_options.add_argument(option)
        
        # Set user agent
        chrome_options.add_argument(f'--user-agent={config.USER_AGENT}')
        
        # Disable automation detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Enhanced performance preferences
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "images": 2,  # Block images
                "plugins": 2,  # Block plugins
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        })
        
        # Rest of setup method remains the same...
        driver = None
        last_error = None
        
        setup_methods = [
            ("WebDriver Manager", self._setup_with_webdriver_manager),
            ("System Chrome", self._setup_with_system_chrome),
            ("Basic Chrome", self._setup_basic_chrome)
        ]
        
        for method_name, setup_func in setup_methods:
            try:
                driver = setup_func(chrome_options)
                if driver:
                    break
            except Exception as e:
                last_error = e
                continue
        
        if not driver:
            raise RuntimeError(f"All Chrome setup methods failed. Last error: {last_error}")
        
        # Set timeouts
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(5)
        
        # Apply stealth settings
        try:
            self._apply_stealth_settings(driver)
        except Exception:
            pass
        
        return driver

    def _setup_with_webdriver_manager(self, chrome_options):
        """Setup using webdriver-manager with enhanced error handling."""
        try:
            # Download and install the correct ChromeDriver
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            
            # Docker environment service configuration
            if os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER'):
                # Docker-specific service options
                service.start_error_message = ""
                service.log_file = "/dev/null"
                # Don't set creation_flags in Linux containers
            else:
                # Add service arguments for better stability on Windows
                service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag for Windows
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Test the driver with a simple command
            driver.execute_script("return navigator.userAgent;")
            
            return driver
            
        except Exception as e:
            raise e

    def _setup_with_system_chrome(self, chrome_options):
        """Setup using system Chrome/Chromium."""
        # Check for Docker environment variables first
        chrome_binary = (os.getenv('CHROME_BIN') or 
                        os.getenv('GOOGLE_CHROME_BIN') or 
                        os.getenv('CHROME_PATH') or 
                        os.getenv('CHROMIUM_PATH'))
        
        # If no environment variable, look for system Chrome/Chromium
        if not chrome_binary:
            chrome_paths = [
                '/usr/bin/google-chrome-stable',
                '/usr/bin/google-chrome',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser'
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break
        
        if not chrome_binary:
            raise RuntimeError("No system Chrome/Chromium found")
        
        chrome_options.binary_location = chrome_binary
        
        # Try to find system ChromeDriver
        driver_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/usr/bin/chromium-driver'
        ]
        
        for driver_path in driver_paths:
            if os.path.exists(driver_path):
                try:
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.set_page_load_timeout(30)
                    return driver
                except Exception:
                    continue
        
        # Fallback to webdriver-manager for system Chrome
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"System Chrome setup failed: {e}")

    def _setup_basic_chrome(self, chrome_options):
        """Basic Chrome setup as last resort."""
        # Remove binary location to use default
        chrome_options.binary_location = None
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            raise Exception(f"Basic Chrome setup failed: {e}")

    def _apply_stealth_settings(self, driver):
        """Apply stealth settings to avoid detection."""
        stealth_script = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Add chrome object
        window.chrome = {
            runtime: {},
        };
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        try:
            driver.execute_script(stealth_script)
        except Exception:
            pass

    def _wait_for_results(self, driver) -> bool:
        """Wait for search results with enhanced selectors."""
        wait = WebDriverWait(driver, 15)  # Increased timeout
        
        # Try each selector with different strategies
        for selector in config.RESULT_SELECTORS:
            try:
                if selector.startswith('#'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.ID, selector[1:])))
                elif selector.startswith('.'):
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selector[1:])))
                else:
                    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                
                if elements:
                    return True
                    
            except TimeoutException:
                continue
            except Exception:
                continue
        
        return False

    def _handle_page_not_loaded(self, driver):
        """Optimized page loading error handling."""
        try:
            # Quick checks first
            page_url = driver.current_url
            
            # Fast content check using JavaScript
            page_info = driver.execute_script("""
                return {
                    title: document.title,
                    bodyText: document.body ? document.body.innerText.slice(0, 200) : '',
                    readyState: document.readyState
                };
            """)
            
            # Check for blocking patterns
            blocking_keywords = ['blocked', 'captcha', 'verify', 'protection', 'cloudflare', 'access denied']
            if any(keyword in page_info['bodyText'].lower() for keyword in blocking_keywords):
                raise RuntimeError("Page blocked or CAPTCHA detected.")
            
            # Verify we're on DuckDuckGo
            if "duckduckgo" not in page_info['title'].lower() and "duckduckgo" not in page_url.lower():
                raise RuntimeError(f"❌ Wrong page loaded. Expected DuckDuckGo, got: {page_info['title']}")
            
            # Quick recovery attempt
            # Single scroll to trigger any lazy loading
            driver.execute_script("window.scrollTo(0, Math.min(500, document.body.scrollHeight));")
            
            # Wait for complete state
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Quick check for results
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article, .result, [data-testid='result']"))
            )
            
            return True
            
        except TimeoutException:
            raise RuntimeError("❌ Could not find search results after recovery attempts")
        except Exception as e:
            raise

    def _click_more_results(self, driver, max_clicks: int, progress_callback=None) -> int:
        """Enhanced more results clicking with progress tracking."""
        pages_retrieved = 1
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        # Initial progress update
        if progress_callback:
            progress_callback(pages_retrieved, max_clicks, "Loaded initial page")
        
        for i in range(max_clicks - 1):
            try:
                # Stop if "No more results found for" appears anywhere on the page
                if driver.execute_script("return document.body.innerText.includes('No more results found for');"):
                    if progress_callback:
                        progress_callback(pages_retrieved, max_clicks, "🛑 No more results found, stopping pagination.")
                    break

                # Update progress at start of each page attempt
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"Loading page {pages_retrieved + 1}...")
                
                wait = WebDriverWait(driver, 20)
                
                # Store initial result count
                initial_results = len(driver.find_elements(By.CSS_SELECTOR, "article, .result, [data-testid='result']"))
                
                # Update progress - scrolling
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"Scrolling to find more results button...")
                
                # Scroll to bottom
                driver.execute_script("""
                    window.scrollTo({
                        top: document.body.scrollHeight - window.innerHeight,
                        behavior: 'smooth'
                    });
                """)
                
                # Wait for page stabilization
                time.sleep(0.3)
                
                # Wait for document ready
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                button_found = False
                
                # Update progress - finding button
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"Looking for 'More results' button...")
                
                for selector in config.MORE_RESULTS_SELECTORS:
                    try:
                        if ':contains(' in selector:
                            text = selector.split("':contains('")[1].split("')")[0]
                            tag = selector.split(':contains(')[0]
                            xpath = f"//{tag}[contains(text(), '{text}')]"
                            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        else:
                            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        if element and element.is_displayed():
                            # Update progress - clicking
                            if progress_callback:
                                progress_callback(pages_retrieved, max_clicks, f"Clicking 'More results' for page {pages_retrieved + 1}...")
                            
                            # Scroll to element with animation
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            
                            # Click using JavaScript
                            driver.execute_script("arguments[0].click();", element)
                            
                            # Update progress - waiting for content
                            if progress_callback:
                                progress_callback(pages_retrieved, max_clicks, f"Waiting for new content to load...")
                            
                            # Wait for new content
                            try:
                                WebDriverWait(driver, 40).until(
                                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "article, .result, [data-testid='result']")) > initial_results
                                )
                                button_found = True
                                pages_retrieved += 1
                                consecutive_failures = 0  # Reset failure counter
                                
                                # Update progress - success
                                if progress_callback:
                                    progress_callback(pages_retrieved, max_clicks, f"✅ Successfully loaded page {pages_retrieved}")
                                break
                            except TimeoutException:
                                consecutive_failures += 1
                                if progress_callback:
                                    progress_callback(pages_retrieved, max_clicks, f"⚠️ Timeout loading page {pages_retrieved + 1}")
                                continue
                                
                    except (NoSuchElementException, TimeoutException):
                        continue
                    except Exception:
                        continue
                
                if not button_found:
                    consecutive_failures += 1
                    if progress_callback:
                        progress_callback(pages_retrieved, max_clicks, f"🔚 No more results available (stopped at page {pages_retrieved})")
                    
                    # Exit early if too many consecutive failures
                    if consecutive_failures >= max_consecutive_failures:
                        if progress_callback:
                            progress_callback(pages_retrieved, max_clicks, f"❌ Stopped after {consecutive_failures} consecutive failures")
                        break
                        
            except Exception as e:
                consecutive_failures += 1
                if progress_callback:
                    progress_callback(pages_retrieved, max_clicks, f"❌ Error loading page {i+2}: {str(e)[:50]}...")
                
                # Exit early if too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    if progress_callback:
                        progress_callback(pages_retrieved, max_clicks, f"❌ Stopped after {consecutive_failures} consecutive failures")
                    break
        
        if progress_callback:
            progress_callback(pages_retrieved, max_clicks, f"🎉 Completed! Loaded {pages_retrieved} pages total")
        
        return pages_retrieved

    def _find_title_link(self, article):
        """Find title link with enhanced selector support."""
        for selector in config.LINK_SELECTORS:
            try:
                link = article.select_one(selector)
                if link and link.get('href'):
                    return link
            except Exception:
                continue
        return None

    def _extract_fallback_links(self, soup) -> list:
        """Enhanced fallback link extraction."""
        results = []
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            try:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Enhanced filtering
                if (title and len(title) > 10 and len(title) < 200 and
                    not href.startswith(('/', '#', 'javascript:', 'mailto:')) and
                    'duckduckgo.com' not in href and
                    any(protocol in href for protocol in ['http://', 'https://']) and
                    not any(skip in href.lower() for skip in ['facebook.com', 'twitter.com', 'linkedin.com'])):
                    
                    # Try to find date in the parent or nearby elements
                    published_date = None
                    try:
                        # Look for date in parent elements
                        parent = link.parent
                        if parent:
                            published_date = self._extract_published_date(parent)
                    except Exception:
                        pass
                    
                    results.append({
                        "title": title,
                        "url": href,
                        "published_date": published_date
                    })
                    
            except Exception:
                continue
        
        return results

    def _extract_published_date(self, article):
        """Extract published date from article with English date handling."""
        try:
            # Debug: Print the article HTML to see what we're working with
            # Commented out for production
            
            date_span = None
            date_text = None
            
            # Primary selector - the exact class from your example
            date_span = article.select_one("span.MILR5XIVy9h75WrLvKiq.qsXMqKZNYEaWqGnWVdoa")
            if date_span:
                date_text = date_span.get_text(strip=True)
            
            if not date_span or not date_text:
                # Enhanced fallback selectors - more comprehensive search
                date_selectors = [
                    # Class-based selectors
                    "span[class*='MILR5XIVy9h75WrLvKiq']",
                    "span[class*='qsXMqKZNYEaWqGnWVdoa']",
                    "span[class*='date']",
                    "span[class*='time']",
                    "span[class*='published']",
                    "span[class*='timestamp']",
                    
                    # Generic time/date elements
                    "time",
                    "time[datetime]",
                    
                    # Common class names
                    ".date",
                    ".published",
                    ".timestamp",
                    ".publish-date",
                    ".post-date",
                    ".article-date",
                ]
                
                for selector in date_selectors:
                    try:
                        date_span = article.select_one(selector)
                        if date_span:
                            date_text = date_span.get_text(strip=True)
                            if date_text:
                                break
                    except Exception as e:
                        # Continue to next selector if this one fails
                        continue
            
            if not date_text:
                # Last resort: search for any text that looks like an English date in the entire article
                article_text = article.get_text()
                
                # Look for English date patterns in the text
                import re
                
                # Pattern for dates like "Mar 19, 2025" or "March 19, 2025"
                english_date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
                matches = re.findall(english_date_pattern, article_text)
                if matches:
                    date_text = matches[0].strip()
                
                # Pattern for "Today"
                elif 'Today' in article_text:
                    date_text = 'Today'
                
                # Pattern for "x days ago" or "x day ago"
                else:
                    days_ago_pattern = r'\b\d+\s+days?\s+ago\b'
                    matches = re.findall(days_ago_pattern, article_text)
                    if matches:
                        date_text = matches[0].strip()
            
            if not date_text:
                return None
            
            # Parse the found date text
            parsed_date = self._parse_english_date(date_text)
            return parsed_date
            
        except Exception:
            return None

    def _parse_english_date(self, date_text: str):
        """Parse English date text and convert to ISO format."""
        try:
            current_date = datetime.datetime.now()
            
            # Clean up the date text
            date_text = date_text.strip()
            
            # Handle "Today"
            if "Today" in date_text or "today" in date_text:
                result = current_date.date().isoformat()
                return result
            
            # Handle "x days ago" or "x day ago"
            days_ago_pattern = r'(\d+)\s+days?\s+ago'
            match = re.search(days_ago_pattern, date_text, re.IGNORECASE)
            if match:
                days_ago = int(match.group(1))
                target_date = current_date - datetime.timedelta(days=days_ago)
                result = target_date.date().isoformat()
                return result
            
            # Handle "Yesterday"
            if "Yesterday" in date_text or "yesterday" in date_text:
                target_date = current_date - datetime.timedelta(days=1)
                result = target_date.date().isoformat()
                return result
            
            # Month name mapping (both abbreviated and full)
            month_mapping = {
                'jan': 1, 'january': 1,
                'feb': 2, 'february': 2,
                'mar': 3, 'march': 3,
                'apr': 4, 'april': 4,
                'may': 5,
                'jun': 6, 'june': 6,
                'jul': 7, 'july': 7,
                'aug': 8, 'august': 8,
                'sep': 9, 'september': 9,
                'oct': 10, 'october': 10,
                'nov': 11, 'november': 11,
                'dec': 12, 'december': 12
            }
            
            # Parse English date formats like "Mar 19, 2025" or "March 19, 2025"
            # Pattern with optional comma
            english_date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
            match = re.search(english_date_pattern, date_text, re.IGNORECASE)
            if match:
                month_name = match.group(1).lower()
                day = int(match.group(2))
                year = int(match.group(3))
                
                # Find month number
                month_num = month_mapping.get(month_name)
                
                if month_num:
                    try:
                        parsed_date = datetime.date(year, month_num, day)
                        result = parsed_date.isoformat()
                        return result
                    except ValueError:
                        return None
            
            # Try parsing other common date formats using strptime
            date_formats = [
                '%B %d, %Y',    # March 19, 2025
                '%b %d, %Y',    # Mar 19, 2025
                '%B %d %Y',     # March 19 2025
                '%b %d %Y',     # Mar 19 2025
                '%Y-%m-%d',     # 2025-03-19
                '%m/%d/%Y',     # 03/19/2025
                '%d/%m/%Y',     # 19/03/2025
                '%Y/%m/%d',     # 2025/03/19
            ]
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.datetime.strptime(date_text, date_format).date()
                    result = parsed_date.isoformat()
                    return result
                except ValueError:
                    continue
            
            # If no pattern matches, return None
            return None
            
        except Exception:
            return None
    
    def _parse_results(self, html: str) -> list:
        """Enhanced result parsing with date extraction."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        # Try to find articles using each selector
        articles = []
        
        for selector in config.RESULT_SELECTORS:
            try:
                found_articles = soup.select(selector)
                if found_articles:
                    articles = found_articles
                    break
            except Exception:
                continue
        
        if not articles:
            return self._extract_fallback_links(soup)
        
        # Extract data from articles
        for i, article in enumerate(articles):
            try:
                link = self._find_title_link(article)
                if link:
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    
                    # Validate result
                    if title and href and len(title) > 5:
                        # Clean up URL if needed
                        if href.startswith('//'):
                            href = 'https:' + href
                        elif href.startswith('/'):
                            href = 'https://duckduckgo.com' + href
                        
                        # Extract published date
                        published_date = self._extract_published_date(article)
                        
                        results.append({
                            "title": title,
                            "url": href,
                            "published_date": published_date
                        })
                        
            except Exception:
                continue
        
        return results

    def scrape(self, query: str, max_pages: int, headless: bool = True, progress_callback=None, start_date=None, end_date=None) -> tuple[pd.DataFrame, int]:
        """
        Enhanced scraping with progress tracking and date range support.
        
        Args:
            query: Search query string
            max_pages: Maximum number of pages to retrieve
            headless: Whether to run browser in headless mode
            progress_callback: Function to call with progress updates
            start_date: Start date for search range (YYYY-MM-DD format)
            end_date: End date for search range (YYYY-MM-DD format)
            
        Returns:
            Tuple of (DataFrame with results, number of pages retrieved)
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        if progress_callback:
            progress_callback(0, max_pages, "🚀 Starting browser...")
        
        # Build URL with optional date range
        url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_"
        
        # Add date range if provided
        if start_date and end_date:
            # Validate date format
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
                url += f"&df={start_date}..{end_date}&ia=web"
            except ValueError as e:
                raise ValueError("Date format must be YYYY-MM-DD")
        
        driver = None
        
        try:
            # Setup driver
            if progress_callback:
                progress_callback(0, max_pages, "🔧 Setting up Chrome driver...")
            
            driver = self._setup_driver(headless)
            
            # Navigate to DuckDuckGo
            if progress_callback:
                progress_callback(0, max_pages, "🌐 Loading DuckDuckGo homepage...")
            
            # Retry logic for Chrome window issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver.get("https://duckduckgo.com/")
                    break
                except Exception:
                    if attempt == max_retries - 1:
                        driver.quit()
                        driver = self._setup_driver(headless)
                        driver.get("https://duckduckgo.com/")
                    else:
                        time.sleep(2)
            
            # Wait for search box
            if progress_callback:
                progress_callback(0, max_pages, "⏳ Waiting for homepage to load...")
            
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "searchbox_input")))
            
            # Navigate to search results
            if progress_callback:
                progress_callback(0, max_pages, f"🔍 Searching for: {query[:50]}...")
            
            # Retry logic for search page navigation
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver.get(url)
                    break
                except Exception:
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Failed to load search page after {max_retries} attempts")
                    else:
                        time.sleep(2)
            
            # Wait for results with multiple fallbacks
            if progress_callback:
                progress_callback(1, max_pages, "⏳ Loading initial search results...")
            
            if not self._wait_for_results(driver):
                if progress_callback:
                    progress_callback(1, max_pages, "🔄 Recovery mode - reloading page...")
                self._handle_page_not_loaded(driver)
            
            # Load additional pages
            if progress_callback:
                progress_callback(1, max_pages, "✅ Initial page loaded, loading more pages...")
            
            pages_retrieved = self._click_more_results(driver, max_pages, progress_callback)
            
            # Get final HTML
            if progress_callback:
                progress_callback(pages_retrieved, max_pages, "📄 Extracting and parsing results...")
            
            html = driver.page_source
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, max_pages, f"❌ Error: {str(e)[:50]}...")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        # Parse results
        results = self._parse_results(html)
        
        df = pd.DataFrame(results)
        
        if progress_callback:
            progress_callback(pages_retrieved, max_pages, f"🎉 Complete! Found {len(df)} results from {pages_retrieved} pages")
        
        return df, pages_retrieved