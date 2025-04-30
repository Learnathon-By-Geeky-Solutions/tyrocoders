import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import List, Dict, Optional, Set, Union

class WebScraper:
    """
    A web scraper that crawls websites to extract product information.
    
    This class implements a recursive crawler that visits web pages starting from a given base URL,
    identifies product pages, and extracts structured product information such as name, price,
    description, and image URL.
    
    Attributes:
        base_url (str): The starting URL for the web crawl.
        max_pages (int): Maximum number of pages to visit during crawling.
        visited_urls (Set[str]): Set of URLs already visited during the crawl.
        products (List[Dict]): List of extracted product information dictionaries.
        logger (logging.Logger): Logger for tracking the crawling process.
    """

    def __init__(self, base_url: str, max_pages: int = 50):
        """
        Initialize the WebScraper with a base URL and crawling parameters.
        
        Args:
            base_url (str): The starting URL for the web crawl.
            max_pages (int, optional): Maximum number of pages to visit. Defaults to 50.
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.products = []
        self.logger = logging.getLogger(__name__)

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage into a BeautifulSoup object.
        
        Args:
            url (str): The URL to fetch and parse.
            
        Returns:
            Optional[BeautifulSoup]: A BeautifulSoup object for the page if successful, None otherwise.
        """
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

    def _extract_product_info(self, url: str) -> Optional[Dict[str, str]]:
        """
        Extract detailed product information from a product page.
        
        Args:
            url (str): The URL of the product page to extract information from.
            
        Returns:
            Optional[Dict[str, str]]: A dictionary containing product details if successful,
                                      None if the page couldn't be fetched or no product data found.
                                      Keys include 'url', 'name', 'price', 'description', 'image_url'.
        """
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

    def _extract_text(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """
        Extract text from the first matching selector in a BeautifulSoup object.
        
        Args:
            soup (BeautifulSoup): The BeautifulSoup object to search within.
            selectors (List[str]): A list of CSS selectors to try in order of preference.
                                  Supports class selectors (.classname), ID selectors (#idname),
                                  and tag names.
            
        Returns:
            str: The extracted text from the first matching selector, or an empty string if no match.
        """
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

    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """
        Extract a product image URL from a BeautifulSoup object.
        
        Args:
            soup (BeautifulSoup): The BeautifulSoup object to search within.
            
        Returns:
            str: The absolute URL of the product image if found, or an empty string otherwise.
        """
        image = soup.find('img', {'src': re.compile(r'.*\.(jpg|jpeg|png|gif)')})
        return urljoin(self.base_url, image['src']) if image and image.get('src') else ''

    def _is_product_page(self, url: str) -> bool:
        """
        Determine if a URL is likely a product page based on common URL patterns.
        
        Args:
            url (str): The URL to evaluate.
            
        Returns:
            bool: True if the URL matches common product page patterns, False otherwise.
        """
        product_patterns = [
            r'/product/',
            r'/products/',
            r'/item/',
            r'/shop/',
            r'\d+$'  # Ends with number
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in product_patterns)

    def crawl(self) -> List[Dict[str, str]]:
        """
        Crawl the website starting from the base URL and extract product information.
        
        This method initiates a recursive crawl of the website, identifying and processing
        product pages to extract structured product information.
        
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing product information.
                                 Each dictionary includes 'url', 'name', 'price',
                                 'description', and 'image_url' keys.
        """
        self.logger.info(f"Starting crawl of {self.base_url}")
        self._crawl_recursive(self.base_url)
        
        self.logger.info(f"Crawl completed. Found {len(self.products)} products.")
        return self.products

    def _crawl_recursive(self, url: str) -> None:
        """
        Recursively crawl the website from a given URL, extracting product information.
        
        This internal method implements the core crawling logic, visiting unvisited URLs,
        identifying product pages, extracting product information, and following links
        within the same domain up to the maximum page limit.
        
        Args:
            url (str): The current URL to process.
        """
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