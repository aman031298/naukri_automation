"""
Naukri.com Search Component - Updated for current UI
"""
import logging
import time
from typing import List, Dict

from src.automation.base_applier import BaseApplier
from src.config.settings import Config

logger = logging.getLogger(__name__)

class NaukriSearch(BaseApplier):
    """Handles Naukri.com job search functionality"""
    
    def __init__(self, browser):
        super().__init__(browser)
        
        # Search specific selectors - Updated for current Naukri UI
        self.search_selectors = {
            'search_input': "input[title='Search'], input.search-job, input[placeholder*='Search'], input[name='qp'], input[class*='search'], #searchKeyword, .search-input",
            'location_input': "input[title='Location'], input.location, input[placeholder*='Location'], input[name='location'], #locationInput, .location-input",
            'search_btn': "button[type='submit'], .search-btn, button:has-text('Search'), #searchButton, .nI-gNb-sb__search-btn",
        }
    
    def search_jobs(self) -> List[Dict]:
        """Search for jobs on Naukri with improved handling"""
        try:
            logger.info(f"🔍 Searching jobs: {Config.JOB_KEYWORDS}")
            
            # Try different search methods
            methods = [
                self._search_via_homepage,
                self._search_via_direct_url,
                self._search_via_jobs_page,
            ]
            
            for method in methods:
                try:
                    jobs = method()
                    if jobs:
                        self.jobs_found = jobs
                        logger.info(f"📊 Found {len(jobs)} jobs")
                        return jobs
                except Exception as e:
                    logger.warning(f"Search method failed: {str(e)}")
                    continue
            
            logger.warning("⚠️ All search methods failed")
            return []
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            self.take_screenshot("search_error")
            return []
    
    def _search_via_homepage(self) -> List[Dict]:
        """Search using the homepage search bar"""
        try:
            logger.info("🔍 Method 1: Searching via homepage...")
            
            # Ensure we're on the homepage
            current_url = self.page.url
            if "naukri.com" not in current_url or "login" in current_url:
                self.page.goto("https://www.naukri.com/", wait_until="domcontentloaded")
                self.browser.human_delay(3, 5)
            
            # Take screenshot before search
            self.take_screenshot("homepage_before_search")
            
            # Find and fill search input using JavaScript
            search_filled = self._fill_search_with_js()
            if not search_filled:
                logger.warning("Could not fill search input")
                return []
            
            # Find and fill location
            self._fill_location_with_js()
            
            # Click search button
            if not self._click_search_button():
                logger.warning("Could not click search button")
                return []
            
            # Wait for results
            self.browser.human_delay(3, 5)
            self.take_screenshot("after_search")
            
            # Extract jobs
            return self._extract_jobs()
            
        except Exception as e:
            logger.warning(f"Homepage search failed: {str(e)}")
            return []
    
    def _fill_search_with_js(self) -> bool:
        """Fill search input using JavaScript (bypasses placeholder interception)"""
        try:
            keywords = " ".join(Config.JOB_KEYWORDS[:3])
            
            # Method 1: Try to find the actual input by attributes
            search_selectors = [
                "input[title='Search']",
                "input[name='qp']",
                "input.search-job",
                "input#searchKeyword",
                ".search-input",
                "input[placeholder*='Search']"
            ]
            
            for selector in search_selectors:
                try:
                    search_input = self.page.locator(selector).first
                    if search_input.count() and search_input.is_visible():
                        # Use JavaScript to set value directly
                        self.page.evaluate(f"""
                            (selector) => {{
                                const el = document.querySelector(selector);
                                if (el) {{
                                    el.value = '{keywords}';
                                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    return true;
                                }}
                                return false;
                            }}
                        """, selector)
                        logger.info(f"✅ Filled search using JS: {keywords}")
                        self.browser.human_delay(0.5, 1)
                        return True
                except:
                    continue
            
            # Method 2: Use click and fill
            search_input = self.page.locator("input[type='text']").first
            if search_input.count() and search_input.is_visible():
                # Try clicking with force
                search_input.click(force=True)
                self.browser.human_delay(0.5, 1)
                search_input.fill(keywords)
                logger.info(f"✅ Filled search using click: {keywords}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"JS fill failed: {str(e)}")
            return False
    
    def _fill_location_with_js(self) -> bool:
        """Fill location input using JavaScript"""
        try:
            location = Config.JOB_LOCATION[0] if isinstance(Config.JOB_LOCATION, list) else Config.JOB_LOCATION
            
            location_selectors = [
                "input[title='Location']",
                "input[name='location']",
                "input.location",
                "input#locationInput",
                ".location-input",
                "input[placeholder*='Location']"
            ]
            
            for selector in location_selectors:
                try:
                    loc_input = self.page.locator(selector).first
                    if loc_input.count() and loc_input.is_visible():
                        # Use JavaScript to set value
                        self.page.evaluate(f"""
                            (selector) => {{
                                const el = document.querySelector(selector);
                                if (el) {{
                                    el.value = '{location}';
                                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    return true;
                                }}
                                return false;
                            }}
                        """, selector)
                        logger.info(f"✅ Filled location using JS: {location}")
                        self.browser.human_delay(0.5, 1)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Location fill failed: {str(e)}")
            return False
    
    def _click_search_button(self) -> bool:
        """Click the search button"""
        try:
            search_btn_selectors = [
                "button[type='submit']",
                ".search-btn",
                "button:has-text('Search')",
                "button:has-text('Find Jobs')",
                "#searchButton",
                ".nI-gNb-sb__search-btn"
            ]
            
            for selector in search_btn_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.count() and btn.is_visible():
                        btn.click(force=True)
                        logger.info(f"✅ Clicked search using: {selector}")
                        return True
                except:
                    continue
            
            # Try pressing Enter
            self.page.keyboard.press("Enter")
            logger.info("✅ Pressed Enter to search")
            return True
            
        except Exception as e:
            logger.warning(f"Search button click failed: {str(e)}")
            return False
    
    def _search_via_direct_url(self) -> List[Dict]:
        """Search using direct URL (most reliable)"""
        try:
            logger.info("🔍 Method 2: Searching via direct URL...")
            
            # Build search URL
            keywords = Config.JOB_KEYWORDS[0].replace(" ", "-").lower()
            location = Config.JOB_LOCATION[0] if isinstance(Config.JOB_LOCATION, list) else Config.JOB_LOCATION
            location = location.replace(" ", "-").lower()
            
            # Try different URL patterns
            urls = [
                f"https://www.naukri.com/{keywords}-jobs-in-{location}",
                f"https://www.naukri.com/{keywords}-jobs",
                f"https://www.naukri.com/jobs-in-{location}",
                f"https://www.naukri.com/jobs?keyword={keywords.replace('-', '+')}&location={location.replace('-', '+')}",
            ]
            
            for url in urls:
                try:
                    logger.info(f"   Trying: {url}")
                    self.page.goto(url, wait_until="domcontentloaded")
                    self.browser.human_delay(3, 5)
                    
                    # Check if jobs are present
                    if self._has_jobs_on_page():
                        logger.info(f"✅ Found jobs on: {url}")
                        self.take_screenshot("direct_search_success")
                        return self._extract_jobs()
                except:
                    continue
            
            return []
            
        except Exception as e:
            logger.warning(f"Direct URL search failed: {str(e)}")
            return []
    
    def _search_via_jobs_page(self) -> List[Dict]:
        """Search via the jobs page"""
        try:
            logger.info("🔍 Method 3: Searching via jobs page...")
            
            # Go to jobs page
            self.page.goto("https://www.naukri.com/jobs", wait_until="domcontentloaded")
            self.browser.human_delay(2, 3)
            
            # Try to find and fill the search form on jobs page
            search_input = self.page.locator("input[placeholder*='Search'], input[type='text']").first
            if search_input.count():
                keywords = " ".join(Config.JOB_KEYWORDS[:2])
                search_input.fill(keywords)
                self.browser.human_delay(1, 2)
                
                # Find location
                loc_input = self.page.locator("input[placeholder*='Location']").first
                if loc_input.count():
                    location = Config.JOB_LOCATION[0] if isinstance(Config.JOB_LOCATION, list) else Config.JOB_LOCATION
                    loc_input.fill(location)
                    self.browser.human_delay(1, 2)
                
                # Click search
                self.page.keyboard.press("Enter")
                self.browser.human_delay(3, 5)
                
                return self._extract_jobs()
            
            return []
            
        except Exception as e:
            logger.warning(f"Jobs page search failed: {str(e)}")
            return []
    
    def _has_jobs_on_page(self) -> bool:
        """Check if jobs are present on the current page"""
        try:
            # Check for job cards
            job_selectors = [
                "article.jobTuple",
                ".jobCard",
                ".job-list-card",
                ".job-card",
                ".result-card",
                ".srp-jobtuple-wrapper",
                "div[class*='jobTuple']"
            ]
            
            for selector in job_selectors:
                if self.page.locator(selector).count() > 0:
                    return True
            
            # Check for no results message
            page_text = self.page.text_content()
            if page_text and ("no jobs" in page_text.lower() or "no results" in page_text.lower()):
                return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Job presence check failed: {str(e)}")
            return False
    
    def _extract_jobs(self) -> List[Dict]:
        """Extract job details from search results"""
        jobs = []
        try:
            # Wait for results with multiple selectors
            job_selectors = [
                "article.jobTuple",
                ".jobCard",
                ".job-list-card",
                ".job-card",
                ".result-card",
                ".srp-jobtuple-wrapper"
            ]
            
            cards = []
            for selector in job_selectors:
                try:
                    found_cards = self.page.locator(selector).all()
                    if found_cards:
                        cards = found_cards
                        logger.info(f"Found {len(cards)} job cards with: {selector}")
                        break
                except:
                    continue
            
            if not cards:
                logger.warning("No job cards found")
                return []
            
            for card in cards:
                try:
                    # Extract job details
                    title = self._extract_text(card, [
                        ".title a",
                        ".job-title",
                        "h2 a",
                        ".jobCard__title",
                        ".job-title-link",
                        "a[class*='title']"
                    ])
                    
                    company = self._extract_text(card, [
                        ".subTitle",
                        ".company",
                        ".job-company",
                        ".company-name",
                        ".jobCard__company",
                        "a[class*='company']"
                    ])
                    
                    location = self._extract_text(card, [
                        ".loc",
                        ".location",
                        ".job-location",
                        ".jobCard__location",
                        "span[class*='location']"
                    ])
                    
                    # Get link
                    link_elem = card.locator("a").first
                    link = link_elem.get_attribute("href") if link_elem.count() else ""
                    
                    if not title or title == "Unknown":
                        continue
                    
                    if self.is_excluded(title, Config.EXCLUDE_KEYWORDS):
                        continue
                    
                    jobs.append({
                        'title': title,
                        'company': company if company != "Unknown" else "Not Specified",
                        'location': location if location != "Unknown" else "Not Specified",
                        'link': link,
                        'status': 'found'
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not parse job card: {str(e)}")
                    continue
            
            logger.info(f"✅ Extracted {len(jobs)} jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Job extraction failed: {str(e)}")
            self.take_screenshot("extract_error")
            return jobs