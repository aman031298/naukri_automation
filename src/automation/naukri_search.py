"""
Naukri.com Search Component - Updated for current UI
"""
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

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

        # Jobs posted before this many days ago are dropped during extraction
        self.max_job_age_days = Config.MAX_JOB_AGE_DAYS
    
    def search_jobs(self) -> List[Dict]:
        """Search for jobs on Naukri with improved handling"""
        try:
            logger.info(f"🔍 Searching jobs: {Config.JOB_KEYWORDS}")

            # Try different search methods. The recommended-jobs feed on
            # the post-login homepage is tried first per user preference —
            # it reflects what Naukri already thinks matches this profile,
            # rather than a fresh keyword search.
            methods = [
                self._search_via_recommended_feed,
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
    
    def _search_via_recommended_feed(self) -> List[Dict]:
        """Read jobs directly from the 'Recommended jobs for you' carousel
        shown on the homepage right after login, instead of running a
        keyword/location search.

        These cards (div.cust-job-tuple inside div.ni-citem) don't carry a
        plain href on their title link — Naukri opens the job page via a
        JS click handler in a new tab — so extraction here works
        differently from the search-results page: title/company/location/
        posted-date come straight from each card's HTML, but the job link
        can only be obtained by clicking through, one candidate at a time,
        until a job clears the exclude-keyword and age filters.
        """
        try:
            logger.info("🔍 Method 0: Reading homepage recommended-jobs feed...")

            current_url = self.page.url
            if "naukri.com" not in current_url or "login" in current_url:
                self.page.goto("https://www.naukri.com/", wait_until="domcontentloaded")
                self.browser.human_delay(3, 5)

            cards = self.page.locator("div.ni-citem .cust-job-tuple").all()
            if not cards:
                logger.warning("No cards found in recommended-jobs feed")
                return []

            logger.info(f"Found {len(cards)} cards in recommended-jobs feed")

            jobs = []
            skipped_old = 0
            for card in cards:
                try:
                    title = self._extract_text(card, ["a.title"])
                    if not title or title == "Unknown":
                        continue

                    if self.is_excluded(title, Config.EXCLUDE_KEYWORDS):
                        continue

                    posted_text = self._extract_text(card, [".job-post-day"])
                    posted_days_ago = self._parse_posted_age(posted_text)
                    if posted_days_ago is not None and posted_days_ago > self.max_job_age_days:
                        skipped_old += 1
                        continue

                    company = self._extract_text(card, [".comp-name"])
                    location = self._extract_text(card, [".loc"])

                    # Clicking the title is the only way to get the real
                    # job URL from this compact card layout — it opens in
                    # a new tab, which we then read and close, leaving the
                    # homepage tab as the active page for the next card.
                    title_link = card.locator("a.title").first
                    try:
                        with self.browser.context.expect_page(timeout=8000) as new_page_info:
                            title_link.click()
                        new_page = new_page_info.value
                        new_page.wait_for_load_state("domcontentloaded", timeout=15000)
                        link = new_page.url
                        new_page.close()
                    except Exception as e:
                        logger.warning(f"Could not resolve link for card '{title}': {str(e)}")
                        continue

                    jobs.append({
                        'title': title,
                        'company': company if company != "Unknown" else "Not Specified",
                        'location': location if location != "Unknown" else "Not Specified",
                        'link': link,
                        'posted': posted_text if posted_text != "Unknown" else "",
                        'posted_days_ago': posted_days_ago,
                        'status': 'found'
                    })

                except Exception as e:
                    logger.warning(f"Could not parse recommended-feed card: {str(e)}")
                    continue

            if skipped_old:
                logger.info(f"⏭️ Skipped {skipped_old} recommended jobs older than {self.max_job_age_days} days")
            logger.info(f"✅ Extracted {len(jobs)} jobs from recommended-jobs feed")
            return jobs

        except Exception as e:
            logger.warning(f"Recommended-feed search failed: {str(e)}")
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
    
    def search_more_jobs(self, page_number: int, exclude_links: Optional[set] = None) -> List[Dict]:
        """Fetch an additional page of keyword/location search results.

        Used when the recommended-jobs feed and page 1 aren't enough to
        reach the target number of confirmed applications — Naukri's
        search-results URLs paginate with a numeric suffix
        (…-jobs-in-<location>-<page>), so each call here pulls a fresh
        batch of candidates instead of reprocessing the same jobs.
        """
        try:
            keywords = Config.JOB_KEYWORDS[0].replace(" ", "-").lower()
            location = Config.JOB_LOCATION[0] if isinstance(Config.JOB_LOCATION, list) else Config.JOB_LOCATION
            location = location.replace(" ", "-").lower()

            suffix = "" if page_number <= 1 else f"-{page_number}"
            url = f"https://www.naukri.com/{keywords}-jobs-in-{location}{suffix}"

            logger.info(f"🔍 Fetching search page {page_number}: {url}")
            self.page.goto(url, wait_until="domcontentloaded")
            self.browser.human_delay(3, 5)

            if not self._has_jobs_on_page():
                logger.info(f"No jobs on page {page_number} — likely past the last page")
                return []

            jobs = self._extract_jobs()
            if exclude_links:
                jobs = [j for j in jobs if j.get('link') not in exclude_links]
            return jobs

        except Exception as e:
            logger.warning(f"search_more_jobs failed for page {page_number}: {str(e)}")
            return []

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
            # div.cust-job-tuple is the actual per-listing card on the current
            # Naukri UI (verified against live search results). Older
            # selectors are kept as fallbacks in case Naukri reverts a UI
            # experiment, but cust-job-tuple must stay first: broader
            # container selectors like .srp-jobtuple-wrapper also match and
            # produce duplicate/nested results if picked first.
            job_selectors = [
                "div.cust-job-tuple",
                "article.jobTuple",
                ".jobCard",
                ".job-list-card",
                ".job-card",
                ".result-card",
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

            skipped_old = 0
            for card in cards:
                try:
                    # Extract job details
                    title = self._extract_text(card, [
                        "h2 a.title",
                        ".title a",
                        ".job-title",
                        "h2 a",
                        ".jobCard__title",
                        ".job-title-link",
                        "a[class*='title']"
                    ])

                    company = self._extract_text(card, [
                        "a.comp-name",
                        ".subTitle",
                        ".company",
                        ".job-company",
                        ".company-name",
                        ".jobCard__company",
                        "a[class*='company']"
                    ])

                    location = self._extract_text(card, [
                        ".locWdth",
                        ".loc-wrap",
                        ".loc",
                        ".location",
                        ".job-location",
                        ".jobCard__location",
                        "span[class*='location']"
                    ])

                    posted_text = self._extract_text(card, [
                        ".job-post-day",
                        "span[class*='job-post-day']",
                    ])

                    # Get link from the title anchor specifically — grabbing
                    # the card's first <a> is unreliable since company/rating
                    # links can appear before the title link in the DOM.
                    link_elem = card.locator("h2 a.title, .title a, h2 a").first
                    link = link_elem.get_attribute("href") if link_elem.count() else ""

                    if not title or title == "Unknown":
                        continue

                    if self.is_excluded(title, Config.EXCLUDE_KEYWORDS):
                        continue

                    posted_days_ago = self._parse_posted_age(posted_text)
                    if posted_days_ago is not None and posted_days_ago > self.max_job_age_days:
                        skipped_old += 1
                        continue

                    jobs.append({
                        'title': title,
                        'company': company if company != "Unknown" else "Not Specified",
                        'location': location if location != "Unknown" else "Not Specified",
                        'link': link,
                        'posted': posted_text if posted_text != "Unknown" else "",
                        'posted_days_ago': posted_days_ago,
                        'status': 'found'
                    })

                except Exception as e:
                    logger.warning(f"Could not parse job card: {str(e)}")
                    continue

            if skipped_old:
                logger.info(f"⏭️ Skipped {skipped_old} jobs older than {self.max_job_age_days} days")
            logger.info(f"✅ Extracted {len(jobs)} jobs")
            return jobs

        except Exception as e:
            logger.error(f"Job extraction failed: {str(e)}")
            self.take_screenshot("extract_error")
            return jobs

    def _parse_posted_age(self, posted_text: str) -> Optional[int]:
        """Convert Naukri's 'posted X ago' text into a day count.

        Returns None when the age can't be determined (e.g. missing text) —
        callers should treat that as "unknown" rather than "old", since
        filtering out a job just because we failed to parse its date would
        silently shrink the result set for the wrong reason.
        """
        if not posted_text or posted_text == "Unknown":
            return None

        text = posted_text.strip().lower()

        if "today" in text or "just now" in text or "few hours" in text:
            return 0

        # Naukri caps its display at "3+ weeks ago" instead of showing an
        # exact count past that point — treat the '+' as "at least this
        # old" so these get excluded rather than falling through to the
        # "unknown age" case (which is treated as not-old, i.e. kept).
        match = re.search(r"(\d+)\+?\s*day", text)
        if match:
            return int(match.group(1))

        match = re.search(r"(\d+)\+?\s*week", text)
        if match:
            return int(match.group(1)) * 7

        match = re.search(r"(\d+)\+?\s*month", text)
        if match:
            return int(match.group(1)) * 30

        return None