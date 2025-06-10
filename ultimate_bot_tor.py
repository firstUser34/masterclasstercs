#!/usr/bin/env python3
"""
Ultimate Web Automation Bot
A complete, single-file Python bot with multiple automation methods.
Easy setup, reliable functionality, works without proxies or complex configuration.
"""

import os
import sys
import time
import random
import logging
import argparse
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urljoin, urlparse
import re

# Auto-install dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import *
except ImportError:
    print("Installing required dependencies...")
   

class UltimateBot:
    """Ultimate web automation bot with multiple methods"""
    
    def __init__(self, use_browser=True, headless=False, stealth=True , use_tor=False):
        """Initialize the bot"""
        self.use_browser = use_browser
        self.headless = headless
        self.stealth = stealth
        self.use_tor = use_tor   # NEW: Store tor usage flag
        self.driver = None
        self.session = requests.Session()
        self.current_url = ""
        self.current_soup = None
        self.setup_logging()
        self.setup_session()
        
    def setup_logging(self):
        """Setup minimal logging - reduced console output"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/bot_activity_{timestamp}.log'
        
        # Configure logging - only file output to reduce console spam
        logging.basicConfig(
            level=logging.INFO,  # Reduced from DEBUG
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8')
                # Removed console handler to reduce output
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.activity_log = []
        
    def _log_activity(self, action: str):
        """Log activity with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        activity = f"[{timestamp}] {action}"
        self.activity_log.append(activity)
        # Reduced console output - only show essential updates
        if any(word in action for word in ["SUCCESS", "COMPLETE", "FAILED", "ERROR"]):
            print(f"📋 {activity}")
        
    def setup_session(self):
        """Setup requests session with stealth headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
        self.session.headers.update(headers)

               # NEW: Enable TOR proxy if requested
        if self.use_tor:
            self.logger.info("Using TOR proxy for requests session.")
            self.session.proxies.update({
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            })
        
    def start_browser(self) -> bool:
        """Start browser if needed"""
        if not self.use_browser or self.driver:
            return True
            
        try:
            self.logger.info("Starting browser...")
            
            # Try multiple browser initialization methods
            methods = [
                self._init_undetected_chrome,
                self._init_standard_chrome
            ]
            
            for method in methods:
                try:
                    if method():
                        if self.stealth:
                            self._apply_stealth()
                        self.logger.info("Browser started successfully")
                        return True
                except Exception as e:
                    self.logger.warning(f"Browser method failed: {e}")
                    continue
                    
            self.logger.warning("Browser initialization failed, using requests mode")
            self.use_browser = False
            return True
            
        except Exception as e:
            self.logger.error(f"Browser start failed: {e}")
            self.use_browser = False
            return True
    
    def _init_undetected_chrome(self) -> bool:
        """Try undetected Chrome"""
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if self.headless:
            options.add_argument('--headless')
        self.driver = uc.Chrome(options=options)
        return True
        
    def _init_standard_chrome(self) -> bool:
        """Try standard Chrome"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        if self.headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        return True
    
    def _apply_stealth(self):
        """Apply stealth measures"""
        try:
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {onConnect: undefined, onMessage: undefined}};
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """
            self.driver.execute_script(stealth_js)
            self.logger.info("Stealth measures applied")
        except Exception as e:
            self.logger.warning(f"Stealth application failed: {e}")
    
    def goto(self, url: str) -> bool:
        """Navigate to URL using browser or requests"""
        try:
            self.logger.info(f"🌐 NAVIGATING TO: {url}")
            self._log_activity(f"GOTO: {url}")
            
            if self.use_browser and self.driver:
                # Browser mode
                self.logger.debug("Using browser mode for navigation")
                self.driver.get(url)
                self.current_url = self.driver.current_url
                html = self.driver.page_source
                self.logger.debug(f"Browser loaded page, HTML length: {len(html)} characters")
            else:
                # Requests mode
                self.logger.debug("Using requests mode for navigation")
                self.logger.debug(f"Request headers: {dict(self.session.headers)}")
                response = self.session.get(url, timeout=30)
                self.logger.debug(f"Response status: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    self.logger.error(f"❌ HTTP ERROR {response.status_code}: {url}")
                    return False
                    
                self.current_url = response.url
                html = response.text
                self.logger.debug(f"Requests loaded page, HTML length: {len(html)} characters")
                
            self.current_soup = BeautifulSoup(html, 'html.parser')
            
            # Log page details
            title = self.get_title()
            self.logger.info(f"✅ PAGE LOADED: {self.current_url}")
            self.logger.info(f"📄 PAGE TITLE: {title}")
            self.logger.debug(f"Page parsing complete with BeautifulSoup")
            
            self._random_delay()
            self._log_activity(f"SUCCESS: Loaded {self.current_url} - Title: {title}")
            return True
            
        except Exception as e:
            error_msg = f"❌ NAVIGATION FAILED: {e}"
            self.logger.error(error_msg)
            self._log_activity(f"ERROR: {error_msg}")
            return False
    
    def find(self, selector: str, timeout: int = 10):
        """Find element by CSS selector"""
        try:
            if self.use_browser and self.driver:
                # Browser mode with wait
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return element
            else:
                # BeautifulSoup mode
                if self.current_soup:
                    return self.current_soup.select_one(selector)
                return None
        except:
            return None
    
    def find_all(self, selector: str) -> List:
        """Find all elements by CSS selector"""
        try:
            if self.use_browser and self.driver:
                return self.driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                if self.current_soup:
                    return self.current_soup.select(selector)
                return []
        except:
            return []
    
    def click(self, element_or_selector, use_js=False) -> bool:
        """Click element (browser mode only)"""
        if not (self.use_browser and self.driver):
            self.logger.warning("Click requires browser mode")
            return False
            
        try:
            if isinstance(element_or_selector, str):
                element = self.find(element_or_selector)
                if not element:
                    return False
            else:
                element = element_or_selector
                
            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
                
            self._random_delay()
            return True
        except Exception as e:
            self.logger.error(f"Click failed: {e}")
            return False
    
    def type_text(self, element_or_selector, text: str, clear=True) -> bool:
        """Type text (browser mode only)"""
        if not (self.use_browser and self.driver):
            self.logger.warning("Type requires browser mode")
            return False
            
        try:
            if isinstance(element_or_selector, str):
                element = self.find(element_or_selector)
                if not element:
                    return False
            else:
                element = element_or_selector
                
            if clear:
                element.clear()
                
            # Human-like typing
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
            self._random_delay()
            return True
        except Exception as e:
            self.logger.error(f"Type failed: {e}")
            return False
    
    def get_text(self, element_or_selector) -> str:
        """Get text from element"""
        try:
            if isinstance(element_or_selector, str):
                element = self.find(element_or_selector)
            else:
                element = element_or_selector
                
            if not element:
                return ""
                
            if self.use_browser and self.driver:
                return element.text if hasattr(element, 'text') else ""
            else:
                return element.get_text(strip=True) if element else ""
        except:
            return ""
    
    def get_attribute(self, element_or_selector, attr: str) -> str:
        """Get attribute from element"""
        try:
            if isinstance(element_or_selector, str):
                element = self.find(element_or_selector)
            else:
                element = element_or_selector
                
            if not element:
                return ""
                
            if self.use_browser and self.driver:
                return element.get_attribute(attr) or ""
            else:
                return element.get(attr, "") if element else ""
        except:
            return ""
    
    def submit_form(self, form_data: Dict[str, str], form_selector: str = "form") -> bool:
        """Submit form with data"""
        try:
            if self.use_browser and self.driver:
                # Browser mode
                form = self.find(form_selector)
                if not form:
                    return False
                    
                for field_name, value in form_data.items():
                    field = self.find(f'input[name="{field_name}"], textarea[name="{field_name}"], select[name="{field_name}"]')
                    if field:
                        self.type_text(field, value)
                        
                # Submit form
                submit_btn = self.find('input[type="submit"], button[type="submit"]')
                if submit_btn:
                    return self.click(submit_btn)
                else:
                    form.submit()
                    return True
            else:
                # Requests mode
                if not self.current_soup:
                    return False
                    
                form = self.current_soup.select_one(form_selector)
                if not form:
                    return False
                    
                # Get form action and method
                action = form.get('action', '')
                method = form.get('method', 'get').lower()
                
                # Build URL
                submit_url = urljoin(self.current_url, action) if action else self.current_url
                
                # Get existing form fields
                form_fields = {}
                for input_elem in form.find_all(['input', 'select', 'textarea']):
                    name = input_elem.get('name')
                    if name:
                        if input_elem.name == 'input':
                            input_type = input_elem.get('type', 'text')
                            if input_type in ['text', 'email', 'password', 'hidden']:
                                form_fields[name] = input_elem.get('value', '')
                        elif input_elem.name == 'textarea':
                            form_fields[name] = input_elem.get_text()
                            
                # Update with provided data
                form_fields.update(form_data)
                
                # Submit
                if method == 'post':
                    response = self.session.post(submit_url, data=form_fields, timeout=30)
                else:
                    response = self.session.get(submit_url, params=form_fields, timeout=30)
                    
                if response.status_code == 200:
                    self.current_url = response.url
                    self.current_soup = BeautifulSoup(response.content, 'html.parser')
                    self._random_delay()
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Form submission failed: {e}")
            return False
    
    def scroll(self, direction="down", pixels=300):
        """Scroll page (browser mode only)"""
        if not (self.use_browser and self.driver):
            return
            
        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
            self._random_delay()
        except Exception as e:
            self.logger.error(f"Scroll failed: {e}")
    
    def screenshot(self, filename=None) -> str:
        """Take screenshot (browser mode only)"""
        if not (self.use_browser and self.driver):
            self.logger.warning("Screenshot requires browser mode")
            return ""
            
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return ""
    
    def search_google(self, query: str) -> bool:
        """Search Google"""
        try:
            self.logger.info(f"Searching Google for: {query}")
            
            if not self.goto("https://www.google.com"):
                return False
                
            # Handle consent if present
            consent_btn = self.find('button[id*="accept"], button[id*="agree"]', timeout=3)
            if consent_btn and self.use_browser:
                self.click(consent_btn)
                
            # Find and use search box
            if self.use_browser and self.driver:
                search_box = self.find('input[name="q"], textarea[name="q"]')
                if search_box:
                    self.type_text(search_box, query)
                    search_box.send_keys(Keys.RETURN)
                    return True
            else:
                # Use form submission for requests mode
                return self.submit_form({'q': query}, 'form[action="/search"]')
                
            return False
            
        except Exception as e:
            self.logger.error(f"Google search failed: {e}")
            return False
    
    def search_bing(self, query: str) -> bool:
        """Search Bing"""
        try:
            self.logger.info(f"Searching Bing for: {query}")
            
            if not self.goto("https://www.bing.com"):
                return False
                
            if self.use_browser and self.driver:
                search_box = self.find('input[name="q"]')
                if search_box:
                    self.type_text(search_box, query)
                    search_box.send_keys(Keys.RETURN)
                    return True
            else:
                return self.submit_form({'q': query}, 'form[action="/search"]')
                
            return False
            
        except Exception as e:
            self.logger.error(f"Bing search failed: {e}")
            return False
    
    def extract_links(self) -> List[Dict[str, str]]:
        """Extract all links from current page with detailed logging"""
        self.logger.info("🔗 EXTRACTING LINKS")
        self._log_activity("EXTRACTING ALL LINKS FROM PAGE")
        
        links = []
        try:
            link_elements = self.find_all('a[href]')
            self.logger.debug(f"Found {len(link_elements)} link elements")
            
            for i, link_elem in enumerate(link_elements):
                try:
                    if self.use_browser and self.driver:
                        href = self.get_attribute(link_elem, 'href')
                        text = self.get_text(link_elem)
                        title = self.get_attribute(link_elem, 'title')
                    else:
                        href = link_elem.get('href', '')
                        text = link_elem.get_text(strip=True)
                        title = link_elem.get('title', '')
                    
                    if href:
                        full_url = urljoin(self.current_url, href)
                        link_data = {
                            'url': full_url,
                            'text': text,
                            'title': title
                        }
                        links.append(link_data)
                        
                        self.logger.debug(f"Link {i+1}: {text[:30]} -> {full_url}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process link {i+1}: {e}")
                    
            self.logger.info(f"✅ EXTRACTED {len(links)} VALID LINKS")
            self._log_activity(f"LINK EXTRACTION COMPLETE - Found {len(links)} links")
                    
        except Exception as e:
            error_msg = f"Link extraction failed: {e}"
            self.logger.error(error_msg)
            self._log_activity(f"ERROR: {error_msg}")
            
        return links
    
    def extract_images(self) -> List[Dict[str, str]]:
        """Extract all images from current page with detailed logging"""
        self.logger.info("🖼️ EXTRACTING IMAGES")
        self._log_activity("EXTRACTING ALL IMAGES FROM PAGE")
        
        images = []
        try:
            img_elements = self.find_all('img')
            self.logger.debug(f"Found {len(img_elements)} image elements")
            
            for i, img in enumerate(img_elements):
                try:
                    if self.use_browser and self.driver:
                        src = self.get_attribute(img, 'src')
                        alt = self.get_attribute(img, 'alt')
                        title = self.get_attribute(img, 'title')
                    else:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        title = img.get('title', '')
                    
                    if src:
                        full_url = urljoin(self.current_url, src)
                        image_data = {
                            'url': full_url,
                            'alt': alt,
                            'title': title
                        }
                        images.append(image_data)
                        
                        self.logger.debug(f"Image {i+1}: {alt[:30]} -> {full_url}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process image {i+1}: {e}")
                    
            self.logger.info(f"✅ EXTRACTED {len(images)} VALID IMAGES")
            self._log_activity(f"IMAGE EXTRACTION COMPLETE - Found {len(images)} images")
            
        except Exception as e:
            error_msg = f"Image extraction failed: {e}"
            self.logger.error(error_msg)
            self._log_activity(f"ERROR: {error_msg}")
            
        return images
    
    def analyze_social_media_content(self) -> Dict[str, Any]:
        """Analyze page for social media specific content"""
        self.logger.info("📱 ANALYZING SOCIAL MEDIA CONTENT")
        self._log_activity("ANALYZING SOCIAL MEDIA PATTERNS")
        
        analysis = {
            'platform': 'unknown',
            'post_type': 'unknown',
            'content_indicators': [],
            'meta_data': {},
            'dynamic_content': False
        }
        
        try:
            url_lower = self.current_url.lower()
            
            # Platform detection
            if 'x.com' in url_lower or 'twitter.com' in url_lower:
                analysis['platform'] = 'twitter/x'
                if '/status/' in url_lower:
                    analysis['post_type'] = 'tweet'
                    
            elif 'facebook.com' in url_lower:
                analysis['platform'] = 'facebook'
                
            elif 'instagram.com' in url_lower:
                analysis['platform'] = 'instagram'
                
            elif 'linkedin.com' in url_lower:
                analysis['platform'] = 'linkedin'
                
            # Check for dynamic content indicators
            if self.current_soup:
                # Look for JavaScript frameworks
                scripts = self.current_soup.find_all('script')
                for script in scripts:
                    if script.get('src'):
                        src = script.get('src', '')
                        if any(framework in src for framework in ['react', 'vue', 'angular', 'client-web']):
                            analysis['dynamic_content'] = True
                            analysis['content_indicators'].append('JavaScript framework detected')
                            break
                
                # Check page text content
                text_content = self.current_soup.get_text()
                if len(text_content.strip()) < 1000:
                    analysis['content_indicators'].append('Minimal text content - likely requires JavaScript')
                
                # Look for meta tags
                meta_tags = self.current_soup.find_all('meta')
                for meta in meta_tags:
                    property_val = meta.get('property', '')
                    name_val = meta.get('name', '')
                    content_val = meta.get('content', '')
                    
                    if property_val.startswith('og:') or property_val.startswith('twitter:'):
                        analysis['meta_data'][property_val] = content_val
                    elif name_val in ['description', 'keywords', 'author']:
                        analysis['meta_data'][name_val] = content_val
                
            self.logger.info(f"🔍 PLATFORM: {analysis['platform']}, TYPE: {analysis['post_type']}")
            self.logger.info(f"🎭 DYNAMIC CONTENT: {analysis['dynamic_content']}")
            self._log_activity(f"SOCIAL MEDIA ANALYSIS - Platform: {analysis['platform']}, Dynamic: {analysis['dynamic_content']}")
            
        except Exception as e:
            error_msg = f"Social media analysis failed: {e}"
            self.logger.error(error_msg)
            self._log_activity(f"ERROR: {error_msg}")
            
        return analysis
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get comprehensive page information with detailed logging"""
        self.logger.info("📊 EXTRACTING PAGE INFORMATION")
        self._log_activity("ANALYZING PAGE DATA")
        
        info = {
            'url': self.current_url,
            'title': '',
            'description': '',
            'keywords': '',
            'links_count': 0,
            'images_count': 0,
            'forms_count': 0,
            'text_length': 0,
            'mode': 'browser' if (self.use_browser and self.driver) else 'requests'
        }
        
        try:
            if self.use_browser and self.driver:
                self.logger.debug("Getting page info from browser mode")
                info['title'] = self.driver.title
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
            else:
                self.logger.debug("Getting page info from requests mode")
                soup = self.current_soup
                
            if soup:
                title_elem = soup.find('title')
                if title_elem and not info['title']:
                    info['title'] = title_elem.get_text(strip=True)
                    
                desc_meta = soup.find('meta', attrs={'name': 'description'})
                info['description'] = desc_meta.get('content', '') if desc_meta else ''
                
                keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
                info['keywords'] = keywords_meta.get('content', '') if keywords_meta else ''
                
                # Count elements with logging
                links = soup.select('a[href]')
                images = soup.select('img')
                forms = soup.select('form')
                
                info['links_count'] = len(links)
                info['images_count'] = len(images)
                info['forms_count'] = len(forms)
                
                text_content = soup.get_text()
                info['text_length'] = len(text_content.strip())
                
                # Log detailed findings
                self.logger.info(f"🔍 FOUND: {info['links_count']} links, {info['images_count']} images, {info['forms_count']} forms")
                self.logger.info(f"📝 TEXT LENGTH: {info['text_length']} characters")
                self._log_activity(f"PAGE ANALYSIS COMPLETE - Links: {info['links_count']}, Images: {info['images_count']}")
                
        except Exception as e:
            error_msg = f"Page info extraction failed: {e}"
            self.logger.error(error_msg)
            self._log_activity(f"ERROR: {error_msg}")
            
        return info
    
    def save_page(self, filename: Optional[str] = None) -> str:
        """Save current page HTML"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"page_{timestamp}.html"
                
            if self.use_browser and self.driver:
                html = self.driver.page_source
            else:
                html = str(self.current_soup) if self.current_soup else ""
                
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
                
            self.logger.info(f"Page saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Save page failed: {e}")
            return ""
    
    def wait_for(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element to appear"""
        if self.use_browser and self.driver:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return True
            except:
                return False
        else:
            # For requests mode, element is already loaded
            return self.find(selector) is not None
    
    def execute_js(self, script: str) -> Any:
        """Execute JavaScript (browser mode only)"""
        if not (self.use_browser and self.driver):
            self.logger.warning("JavaScript execution requires browser mode")
            return None
            
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"JavaScript execution failed: {e}")
            return None
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get cookies"""
        try:
            if self.use_browser and self.driver:
                return self.driver.get_cookies()
            else:
                # Convert requests cookies to dict format
                cookies = []
                for cookie in self.session.cookies:
                    cookies.append({
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path
                    })
                return cookies
        except Exception as e:
            self.logger.error(f"Get cookies failed: {e}")
            return []
    
    def get_current_url(self) -> str:
        """Get current URL"""
        return self.current_url
    
    def get_title(self) -> str:
        """Get page title"""
        try:
            if self.use_browser and self.driver:
                return self.driver.title
            else:
                if self.current_soup:
                    title_elem = self.current_soup.find('title')
                    return title_elem.get_text(strip=True) if title_elem else ""
                return ""
        except:
            return ""
    
    def _random_delay(self, min_delay=0.5, max_delay=2.0):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def close(self):
        """Close browser and session"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed")
            self.session.close()
            self.logger.info("Session closed")
        except Exception as e:
            self.logger.error(f"Close failed: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.start_browser()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

def interactive_mode():
    """Interactive mode for testing"""
    print("\n🚀 Ultimate Web Bot - Interactive Mode")
    print("Commands:")
    print("  goto <url>           - Navigate to URL")
    print("  search <query>       - Search on Google")
    print("  bing <query>         - Search on Bing")
    print("  find <selector>      - Find element by CSS selector")
    print("  text <selector>      - Get text from element")
    print("  click <selector>     - Click element (browser mode)")
    print("  type <selector> <text> - Type text (browser mode)")
    print("  scroll <direction>   - Scroll page (browser mode)")
    print("  screenshot           - Take screenshot (browser mode)")
    print("  links                - Extract all links")
    print("  images               - Extract all images")
    print("  info                 - Get page information")
    print("  save                 - Save current page")
    print("  cookies              - Get cookies")
    print("  js <script>          - Execute JavaScript (browser mode)")
    print("  mode                 - Switch between browser/requests mode")
    print("  quit                 - Exit")
    print()
    
    # Configuration
    use_browser = input("Use browser mode? (y/n): ").lower() == 'y'
    headless = False
    if use_browser:
        headless = input("Run headless? (y/n): ").lower() == 'y'
    
    with UltimateBot(use_browser=args.browser, headless=args.headless, use_tor=args.tor) as bot:
        print(f"Started in {'browser' if bot.use_browser else 'requests'} mode")
        
        while True:
            try:
                command = input("\n> ").strip()
                if not command:
                    continue
                    
                parts = command.split(maxsplit=2)
                cmd = parts[0].lower()
                
                if cmd == 'quit':
                    break
                elif cmd == 'goto' and len(parts) > 1:
                    success = bot.goto(parts[1])
                    print(f"Navigation: {'Success' if success else 'Failed'}")
                elif cmd == 'search' and len(parts) > 1:
                    query = ' '.join(parts[1:])
                    success = bot.search_google(query)
                    print(f"Google search: {'Success' if success else 'Failed'}")
                elif cmd == 'bing' and len(parts) > 1:
                    query = ' '.join(parts[1:])
                    success = bot.search_bing(query)
                    print(f"Bing search: {'Success' if success else 'Failed'}")
                elif cmd == 'find' and len(parts) > 1:
                    element = bot.find(parts[1])
                    print(f"Found: {element is not None}")
                elif cmd == 'text' and len(parts) > 1:
                    text = bot.get_text(parts[1])
                    print(f"Text: {text[:200]}")
                elif cmd == 'click' and len(parts) > 1:
                    success = bot.click(parts[1])
                    print(f"Click: {'Success' if success else 'Failed'}")
                elif cmd == 'type' and len(parts) > 2:
                    success = bot.type_text(parts[1], parts[2])
                    print(f"Type: {'Success' if success else 'Failed'}")
                elif cmd == 'scroll':
                    direction = parts[1] if len(parts) > 1 else 'down'
                    bot.scroll(direction)
                    print(f"Scrolled {direction}")
                elif cmd == 'screenshot':
                    filename = bot.screenshot()
                    print(f"Screenshot: {filename}")
                elif cmd == 'links':
                    links = bot.extract_links()
                    print(f"Found {len(links)} links")
                    for link in links[:10]:
                        print(f"  {link['text'][:50]} -> {link['url']}")
                elif cmd == 'images':
                    images = bot.extract_images()
                    print(f"Found {len(images)} images")
                    for img in images[:10]:
                        print(f"  {img['alt'][:30]} -> {img['url']}")
                elif cmd == 'info':
                    info = bot.get_page_info()
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                elif cmd == 'save':
                    filename = bot.save_page()
                    print(f"Saved: {filename}")
                elif cmd == 'cookies':
                    cookies = bot.get_cookies()
                    print(f"Found {len(cookies)} cookies")
                    for cookie in cookies[:5]:
                        print(f"  {cookie.get('name', 'N/A')}: {cookie.get('value', 'N/A')[:30]}")
                elif cmd == 'js' and len(parts) > 1:
                    script = ' '.join(parts[1:])
                    result = bot.execute_js(script)
                    print(f"Result: {result}")
                elif cmd == 'mode':
                    mode = "browser" if bot.use_browser and bot.driver else "requests"
                    print(f"Current mode: {mode}")
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

def process_multiple_urls(urls_list, browser_mode=False, extract_links=False, extract_images=False, save_pages=False , use_tor=False):
    """
    Process multiple URLs efficiently
    
    Usage:
    urls = [ "https://x.com/Hitansh54/status/1931754193489957133", "https://x.com/Hitansh54/status/1931410374139777334", "https://x.com/Hitansh54/status/1931399970139296013"]
    process_multiple_urls(urls, extract_links=True, save_pages=True)
    """
    results = []
    
    with UltimateBot(use_browser=browser_mode , use_tor=use_tor) as bot:
        for i, url in enumerate(urls_list, 1):
            print(f"\n[{i}/{len(urls_list)}] Processing: {url}")
            
            if bot.goto(url):
                result = {
                    'url': url,
                    'success': True,
                    'info': bot.get_page_info(),
                    'links': bot.extract_links() if extract_links else [],
                    'images': bot.extract_images() if extract_images else [],
                    'saved_file': bot.save_page() if save_pages else None
                }
                
                # Show basic info
                print(f"  Title: {result['info']['title']}")
                print(f"  Links: {result['info']['links_count']}")
                print(f"  Images: {result['info']['images_count']}")
                
            else:
                result = {'url': url, 'success': False}
                print(f"  Failed to load: {url}")
            
            results.append(result)
    
    return results

def main():
    """
    Main function with enhanced multi-URL support
    
    CHANGE URLS HERE - Edit the urls_to_process list below:
    """
    
    # ============== CHANGE YOUR URLS HERE ==============
    # Add your URLs to this list:
    urls_to_process = [
        "https://x.com/Hitansh54/status/1931754193489957133",
         "https://x.com/Hitansh54/status/1931410374139777334",
        "https://x.com/Hitansh54/status/1931399970139296013",
        "https://x.com/Hitansh54/status/1930697596261060654",
    ]
    # ===================================================
    
    parser = argparse.ArgumentParser(description='Ultimate Web Automation Bot')
    parser.add_argument('--url', help='Single URL to visit')
    parser.add_argument('--urls', nargs='+', help='Multiple URLs to process')
    parser.add_argument('--search', help='Search query for Google')
    parser.add_argument('--bing', help='Search query for Bing')
    parser.add_argument('--browser', action='store_true', help='Use browser mode')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--screenshot', action='store_true', help='Take screenshot')
    parser.add_argument('--info', action='store_true', help='Show page info')
    parser.add_argument('--save', action='store_true', help='Save page')
    parser.add_argument('--links', action='store_true', help='Extract links')
    parser.add_argument('--images', action='store_true', help='Extract images')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--batch', action='store_true', help='Process URLs from the urls_to_process list')
    parser.add_argument('--tor', action='store_true', help='Route traffic via Tor')
    # use_tor=args.tor  
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    if args.batch:
        # Process multiple URLs from the predefined list
        print(f"Processing {len(urls_to_process)} URLs in batch mode...")
        process_multiple_urls(
            urls_to_process, 
            browser_mode=args.browser,
            extract_links=args.links,
            extract_images=args.images,
            save_pages=args.save ,
              use_tor=args.tor  # 🔥 add this line
        )
        return
    
    if args.urls:
        # Process multiple URLs from command line
        print(f"Processing {len(args.urls)} URLs...")
        process_multiple_urls(
            args.urls,
            browser_mode=args.browser,
            extract_links=args.links,
            extract_images=args.images,
            save_pages=args.save
        )
        return
    
    # Single URL processing
    try:
        with UltimateBot(use_browser=args.browser, headless=args.headless) as bot:
            if args.search:
                bot.search_google(args.search)
            elif args.bing:
                bot.search_bing(args.bing)
            elif args.url:
                bot.goto(args.url)
            else:
                # Use the first URL from the list if no URL specified
                bot.goto(urls_to_process[0] if urls_to_process else "https://www.google.com")
            
            if args.info:
                info = bot.get_page_info()
                print("\nPage Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            
            if args.links:
                links = bot.extract_links()
                print(f"\nFound {len(links)} links:")
                for link in links[:20]:
                    print(f"  {link['text'][:60]} -> {link['url']}")
            
            if args.images:
                images = bot.extract_images()
                print(f"\nFound {len(images)} images:")
                for img in images[:20]:
                    print(f"  {img['alt'][:40]} -> {img['url']}")
            
            if args.save:
                filename = bot.save_page()
                print(f"Page saved: {filename}")
                
            if args.screenshot:
                filename = bot.screenshot()
                print(f"Screenshot: {filename}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()