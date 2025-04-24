import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import List, Dict

class WebScraper:
    def __init__(self, base_url: str, max_pages: int = 50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.products = []
        self.logger = logging.getLogger(__name__)

    def _get_soup(self, url: str):
        """Fetch and parse a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_product_info(self, url: str):
        """Extract detailed product information from a page"""
        soup = self._get_soup(url)
        if not soup:
            return None

        # Customizable product extraction (adjust selectors as needed)
        product = {
            'url': url,
            'name': self._extract_text(soup, ['h1', 'title', '.product-title']),
            'price': self._extract_text(soup, ['.price', '.product-price', 'span[data-price]']),
            'description': self._extract_text(soup, ['.description', '#product-description', 'meta[name="description"]']),
            'image_url': self._extract_image_url(soup)
        }

        # Filter out empty products
        if product['name'] and product['price']:
            return product
        return None

    def _extract_text(self, soup, selectors):
        """Extract text from first matching selector"""
        for selector in selectors:
            try:
                if selector.startswith('.'):
                    element = soup.find(class_=selector[1:])
                elif selector.startswith('#'):
                    element = soup.find(id=selector[1:])
                else:
                    element = soup.find(selector)
                
                if element:
                    # Handle different element types
                    if element.name == 'meta':
                        return element.get('content', '').strip()
                    return element.get_text(strip=True)
            except Exception:
                continue
        return ''

    def _extract_image_url(self, soup):
        """Extract product image URL"""
        image = soup.find('img', {'src': re.compile(r'.*\.(jpg|jpeg|png|gif)')})
        return urljoin(self.base_url, image['src']) if image and image.get('src') else ''

    def _is_product_page(self, url):
        """Determine if a URL is likely a product page"""
        product_patterns = [
            r'/product/',
            r'/products/',
            r'/item/',
            r'/shop/',
            r'\d+$'  # Ends with number
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in product_patterns)

    def crawl(self):
        """Crawl website and extract products"""
        self.logger.info(f"Starting crawl of {self.base_url}")
        self._crawl_recursive(self.base_url)
        
        self.logger.info(f"Crawl completed. Found {len(self.products)} products.")
        return self.products

    def _crawl_recursive(self, url):
        """Recursive website crawling"""
        # Prevent infinite crawling
        if (len(self.visited_urls) >= self.max_pages or 
            url in self.visited_urls or 
            not url.startswith(self.base_url)):
            return

        self.visited_urls.add(url)

        try:
            soup = self._get_soup(url)
            if not soup:
                return

            # Check if product page
            if self._is_product_page(url):
                product = self._extract_product_info(url)
                if product:
                    self.products.append(product)

            # Find and follow links
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                
                # Ensure URL is within the same domain
                if (urlparse(next_url).netloc == urlparse(self.base_url).netloc and 
                    next_url not in self.visited_urls):
                    self._crawl_recursive(next_url)

        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")