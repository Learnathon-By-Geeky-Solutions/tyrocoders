import asyncio
import aiohttp
import json
import re
import random
import xml.etree.ElementTree as ET
import gzip
from io import BytesIO
from typing import Dict, Any, Optional, List, Tuple
from bs4 import BeautifulSoup

from training.find_sitemap import find_sitemaps

def extract_images(product_data):
    """
    Extract image URLs from product data
    
    Args:
        product_data (dict): Product data containing image information
    
    Returns:
        List of image URLs
    """
    image_field = product_data.get("image", "")
    images = []
    
    if isinstance(image_field, list):
        for item in image_field:
            if isinstance(item, dict) and "url" in item:
                images.append(item["url"])
            elif isinstance(item, str):
                images.append(item)
    elif isinstance(image_field, dict):
        if "url" in image_field:
            images.append(image_field["url"])
    elif isinstance(image_field, str):
        images.append(image_field)
    
    return images

class SitemapUrlExtractor:
    """
    A utility class for extracting URLs from sitemaps
    """
    @staticmethod
    async def extract_sitemap_urls(
        sitemap_url: str, 
        session: aiohttp.ClientSession, 
        check_products: bool = True, 
        sample_size: int = 5
    ) -> List[str]:
        """
        Extract URLs from a sitemap, with optional product page validation
        
        Args:
            sitemap_url (str): URL of the sitemap
            session (aiohttp.ClientSession): HTTP session
            check_products (bool): Whether to validate product pages
            sample_size (int): Number of URLs to sample for product validation
        
        Returns:
            List of extracted URLs
        """
        try:
            async with session.get(sitemap_url) as response:
                if response.status != 200:
                    print(f"Error fetching sitemap: Status {response.status}")
                    return []
                
                # Handle gzipped sitemaps
                content = await SitemapUrlExtractor._get_sitemap_content(response, sitemap_url)
                
                # Process sitemap index or regular sitemap
                if '<sitemapindex' in content:
                    return await SitemapUrlExtractor._process_sitemap_index(
                        content, session, check_products, sample_size
                    )
                else:
                    return await SitemapUrlExtractor._process_sitemap(
                        content, session, check_products, sample_size
                    )
        
        except Exception as e:
            print(f"Error extracting URLs from sitemap {sitemap_url}: {e}")
            return []

    @staticmethod
    async def _get_sitemap_content(response, sitemap_url: str) -> str:
        """
        Get sitemap content, handling gzipped files
        
        Args:
            response: HTTP response
            sitemap_url (str): URL of the sitemap
        
        Returns:
            Decoded sitemap content
        """
        if sitemap_url.endswith('.gz'):
            compressed_content = await response.read()
            with gzip.GzipFile(fileobj=BytesIO(compressed_content)) as gz:
                return gz.read().decode('utf-8')
        else:
            return await response.text()

    @staticmethod
    async def _process_sitemap_index(
        content: str, 
        session: aiohttp.ClientSession, 
        check_products: bool, 
        sample_size: int
    ) -> List[str]:
        """
        Process sitemap index and extract URLs from child sitemaps
        """
        root = ET.fromstring(content)
        namespace = SitemapUrlExtractor._get_namespace(root)
        
        sitemap_urls = [
            loc.text for loc in root.findall(f'{namespace}sitemap/{namespace}loc') 
            if loc is not None
        ]
        
        all_urls = []
        for child_sitemap in sitemap_urls:
            print(f"Processing child sitemap: {child_sitemap}")
            child_urls = await SitemapUrlExtractor.extract_sitemap_urls(
                child_sitemap, session, check_products, sample_size
            )
            all_urls.extend(child_urls)
        
        return all_urls

    @staticmethod
    async def _process_sitemap(
        content: str, 
        session: aiohttp.ClientSession, 
        check_products: bool, 
        sample_size: int
    ) -> List[str]:
        """
        Process regular sitemap and extract URLs
        """
        root = ET.fromstring(content)
        namespace = SitemapUrlExtractor._get_namespace(root)
        
        urls = [
            loc.text for loc in root.findall(f'{namespace}url/{namespace}loc') 
            if loc is not None
        ]
        
        print(f"Found {len(urls)} URLs in sitemap")
        
        if check_products and urls:
            contains_products = await SitemapUrlExtractor._check_sitemap_contains_products(
                urls, session, sample_size
            )
            if not contains_products:
                print(f"Skipping sitemap as it doesn't appear to contain product pages")
                return []
        
        return urls

    @staticmethod
    def _get_namespace(root: ET.Element) -> str:
        """
        Extract XML namespace from root element
        """
        match = re.match(r'({.*})', root.tag)
        return match.group(1) if match else ''

    @staticmethod
    async def _check_sitemap_contains_products(
        urls: List[str], 
        session: aiohttp.ClientSession, 
        sample_size: int = 5
    ) -> bool:
        """
        Check if sitemap contains product pages
        """
        if not urls:
            return False
        
        sample_size = min(sample_size, len(urls))
        sample_urls = random.sample(urls, sample_size)
        
        product_count = sum(
            await asyncio.gather(
                *[SitemapUrlExtractor._is_product_page(url, session) for url in sample_urls]
            )
        )
        
        product_ratio = product_count / sample_size
        print(f"Sampled {sample_size} URLs, found {product_count} product pages (ratio: {product_ratio:.2f})")
        
        return product_ratio > 0

    @staticmethod
    async def _is_product_page(url: str, session: aiohttp.ClientSession) -> bool:
        """
        Determine if a page is a product page
        """
        try:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    print(f"Error accessing {url}: Status {response.status}")
                    return False
                
                text = await response.text()
                product_indicators = [
                    '"@type": "Product"',
                    "'@type': 'Product'",
                    '"@type":"Product"',
                    "'@type':'Product'",
                    'type="Product"',
                    "type='Product'"
                ]
                
                for indicator in product_indicators:
                    if indicator in text:
                        print(f"Found product page: {url} (indicator: {indicator})")
                        return True
                
                print(f"Not a product page: {url}")
                return False
        
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return False

class ProductSchemaExtractor:
    """
    A utility class for extracting product schema from HTML
    """
    PRODUCT_TYPE_KEY = "@type"
    PRODUCT_TYPE_VALUE = "Product"
    PRICE_TYPE_LIST = "https://schema.org/ListPrice"

    @classmethod
    def extract_product_schema_from_text(cls, url: str, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract product schema from HTML text
        """
        soup = BeautifulSoup(text, 'html.parser')
        scripts = soup.find_all("script", type="application/ld+json")
        
        product_data = cls._find_product_schema(url, scripts)
        
        if not product_data:
            print(f"No product schema found for {url}")
            return None
        
        return cls._parse_product_details(url, product_data)

    @classmethod
    def _find_product_schema(cls, url: str, scripts: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Find product schema in list of script tags
        """
        for script in scripts:
            try:
                data = json.loads(script.string)
                product_data = cls._extract_product_from_data(data)
                
                if product_data:
                    print(f"Extracted product schema from {url}")
                    return product_data
            
            except Exception as e:
                print(f"Error parsing JSON from script in {url}: {e}")
        
        return None

    @classmethod
    def _extract_product_from_data(cls, data: Any) -> Optional[Dict[str, Any]]:
        """
        Extract product schema from different data structures
        """
        if isinstance(data, list):
            return next((entry for entry in data 
                         if entry.get(cls.PRODUCT_TYPE_KEY) == cls.PRODUCT_TYPE_VALUE), None)
        
        if isinstance(data, dict):
            if "@graph" in data:
                return next((entry for entry in data["@graph"] 
                             if entry.get(cls.PRODUCT_TYPE_KEY) == cls.PRODUCT_TYPE_VALUE), None)
            
            if data.get(cls.PRODUCT_TYPE_KEY) == cls.PRODUCT_TYPE_VALUE:
                return data
        
        return None

    @classmethod
    def _parse_product_details(cls, url: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse detailed product information
        """
        product_info = {
            "url": url,
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "sku": product_data.get("sku", ""),
            "image": extract_images(product_data),
            "originalPrice": "",
            "discount": "",
            "priceCurrency": "",
            "availability": "",
            "seller": "",
            "ratingValue": "",
            "ratingCount": ""
        }

        offers = product_data.get("offers")
        if offers:
            cls._process_offers(offers, product_info)

        cls._process_aggregate_rating(product_data, product_info)
        
        return product_info

    @classmethod
    def _process_offers(cls, offers: Any, product_info: Dict[str, Any]) -> None:
        """
        Process product offers and update product_info
        """
        offer = offers[0] if isinstance(offers, list) else offers
        
        original_price, discount, price_currency = cls._extract_pricing(offer)
        
        product_info.update({
            "originalPrice": original_price,
            "discount": discount,
            "priceCurrency": price_currency,
            "availability": cls._parse_availability(offer.get("availability", "")),
            "seller": cls._parse_seller(offer.get("seller", {}))
        })

    @classmethod
    def _extract_pricing(cls, offer: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Extract pricing details from offer
        """
        price_spec = offer.get("priceSpecification", [])
        original_price = discount = price_currency = ""
        
        if isinstance(price_spec, list) and price_spec:
            for spec in price_spec:
                if spec.get("priceType") == cls.PRICE_TYPE_LIST:
                    original_price = spec.get("price", "")
                    price_currency = spec.get("priceCurrency", "")
                else:
                    discount = spec.get("price", "")
                    price_currency = price_currency or spec.get("priceCurrency", "")
        else:
            original_price = offer.get("price", "")
            price_currency = offer.get("priceCurrency", "")
        
        return original_price, discount, price_currency

    @staticmethod
    def _parse_availability(availability: str) -> str:
        """
        Parse product availability
        """
        if "InStock" in availability:
            return "In Stock"
        elif "OutOfStock" in availability:
            return "Out of Stock"
        return availability

    @staticmethod
    def _parse_seller(seller: Any) -> str:
        """
        Parse seller information
        """
        return seller.get("name", "") if isinstance(seller, dict) else seller

    @classmethod
    def _process_aggregate_rating(cls, product_data: Dict[str, Any], product_info: Dict[str, Any]) -> None:
        """
        Process aggregate rating information
        """
        aggregate_rating = product_data.get("aggregateRating")
        if aggregate_rating and isinstance(aggregate_rating, dict):
            product_info.update({
                "ratingValue": aggregate_rating.get("ratingValue", ""),
                "ratingCount": aggregate_rating.get("ratingCount", "")
            })

async def fetch_and_extract(url, session, semaphore):
    """
    Fetch a URL and extract product schema
    """
    async with semaphore:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    print(f"Error accessing {url}: Status {response.status}")
                    return None
                text = await response.text()
                return ProductSchemaExtractor.extract_product_schema_from_text(url, text)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

async def scrape_products(
    sitemap_url, 
    scrape_limit=float('inf'), 
    sample_size=5, 
    max_concurrent=20
):
    """
    Scrape product information from a sitemap
    """
    async with aiohttp.ClientSession() as session:
        urls = await SitemapUrlExtractor.extract_sitemap_urls(
            sitemap_url, 
            session, 
            check_products=True, 
            sample_size=sample_size
        )
        print(f"Total URLs extracted from sitemaps with product content: {len(urls)}\n")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        products = []
        tasks = []
        count = 0
        
        for url in urls:
            if count >= scrape_limit:
                break
            tasks.append(fetch_and_extract(url, session, semaphore))
            count += 1

        results = await asyncio.gather(*tasks)
        for product_info in results:
            if product_info:
                products.append(product_info)

        print(f"Successfully processed {len(products)} product pages.")
        return products

async def scrape_from_website(
    website_url: str, 
    scrape_limit: int = 5, 
    sample_size: int = 3, 
    max_concurrent: int = 20
):
    """
    Scrape product information from a website
    """
    sitemap_urls = find_sitemaps(website_url)
    if sitemap_urls:
        first_sitemap = sitemap_urls[0]
        products = await scrape_products(
            first_sitemap,
            scrape_limit=scrape_limit,
            sample_size=sample_size,
            max_concurrent=max_concurrent
        )
        return products
    else:
        print(f"No sitemap URLs found for {website_url}.")
        return []
