import asyncio
import nest_asyncio
import aiohttp
import json
import re
import random
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from training.find_sitemap import find_sitemaps

current_loop = asyncio.get_event_loop()
if type(current_loop).__name__ != "Loop" or "uvloop" not in current_loop.__class__.__module__:
    nest_asyncio.apply()
else:
    print("Using uvloop; nest_asyncio patching skipped.")

async def is_product_page(url, session):
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
                    print(f"Found product page (sampling): {url} (indicator: {indicator})")
                    return True
            print(f"Not a product page (sampling): {url}")
            return False
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False

async def check_sitemap_contains_products(urls, session, sample_size=5):
    if not urls:
        return False
    sample_size = min(sample_size, len(urls))
    sample_urls = random.sample(urls, sample_size)
    product_count = 0
    for url in sample_urls:
        if await is_product_page(url, session):
            product_count += 1
    product_ratio = product_count / sample_size
    print(f"Sampled {sample_size} URLs, found {product_count} product pages (ratio: {product_ratio:.2f})\n")
    return product_ratio > 0

async def extract_sitemap_urls(sitemap_url, session, check_products=True, sample_size=5):
    try:
        async with session.get(sitemap_url) as response:
            if response.status != 200:
                print(f"Error fetching sitemap: Status {response.status}")
                return []
            # content = await response.text()
            if sitemap_url.endswith('.gz'):
                import gzip
                from io import BytesIO
                compressed_content = await response.read()
                with gzip.GzipFile(fileobj=BytesIO(compressed_content)) as gz:
                    content = gz.read().decode('utf-8')
            else:
                content = await response.text()
                
            if '<sitemapindex' in content:
                root = ET.fromstring(content)
                namespace = re.match(r'({.*})', root.tag).group(1) if re.match(r'({.*})', root.tag) else ''
                sitemap_urls = []
                for sitemap in root.findall(f'{namespace}sitemap'):
                    loc = sitemap.find(f'{namespace}loc')
                    if loc is not None:
                        sitemap_urls.append(loc.text)
                all_urls = []
                for child_sitemap in sitemap_urls:
                    print(f"Processing child sitemap: {child_sitemap}")
                    child_urls = await extract_sitemap_urls(child_sitemap, session, check_products, sample_size)
                    all_urls.extend(child_urls)
                return all_urls
            else:
                root = ET.fromstring(content)
                namespace = re.match(r'({.*})', root.tag).group(1) if re.match(r'({.*})', root.tag) else ''
                urls = []
                for url_element in root.findall(f'{namespace}url'):
                    loc = url_element.find(f'{namespace}loc')
                    if loc is not None:
                        urls.append(loc.text)
                print(f"Found {len(urls)} URLs in sitemap")
                if check_products and urls:
                    contains_products = await check_sitemap_contains_products(urls, session, sample_size)
                    if not contains_products:
                        print(f"Skipping sitemap {sitemap_url} as it doesn't appear to contain product pages\n")
                        return []
                return urls
    except Exception as e:
        print(f"Error extracting URLs from sitemap {sitemap_url}: {e}\n")
        return []

def extract_images(product_data):
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

def extract_product_schema_from_text(url, text):
    soup = BeautifulSoup(text, 'html.parser')
    scripts = soup.find_all("script", type="application/ld+json")
    product_data = None
    for script in scripts:
        try:
            data = json.loads(script.string)
            # Handle a list of objects or a single object.
            if isinstance(data, list):
                for entry in data:
                    if entry.get("@type") == "Product":
                        product_data = entry
                        break
            elif isinstance(data, dict):
                if "@graph" in data:
                    for entry in data["@graph"]:
                        if entry.get("@type") == "Product":
                            product_data = entry
                            break
                elif data.get("@type") == "Product":
                    product_data = data
            if product_data:
                print(f"Extracted product schema from {url}")
                break
        except Exception as e:
            print(f"Error parsing JSON from script in {url}: {e}")
            continue

    if not product_data:
        print(f"No product schema found for {url}")
        return None

    product_info = {
        "url": url,
        "name": product_data.get("name", ""),
        "description": product_data.get("description", ""),
        "sku": product_data.get("sku", ""),
        "image": extract_images(product_data),  # This returns a list of image URLs.
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
        if isinstance(offers, list):
            offer = offers[0]
        else:
            offer = offers

        original_price = ""
        discount = ""
        price_currency = ""
        price_spec = offer.get("priceSpecification")
        if isinstance(price_spec, list) and price_spec:
            for spec in price_spec:
                if spec.get("priceType") == "https://schema.org/ListPrice":
                    original_price = spec.get("price", "")
                    price_currency = spec.get("priceCurrency", "")
                else:
                    discount = spec.get("price", "")
                    if not price_currency:
                        price_currency = spec.get("priceCurrency", "")
        else:
            original_price = offer.get("price", "")
            price_currency = offer.get("priceCurrency", "")

        product_info["originalPrice"] = original_price
        product_info["discount"] = discount
        product_info["priceCurrency"] = price_currency

        availability = offer.get("availability", "")
        if "InStock" in availability:
            product_info["availability"] = "In Stock"
        elif "OutOfStock" in availability:
            product_info["availability"] = "Out of Stock"
        else:
            product_info["availability"] = availability

        seller = offer.get("seller", {})
        if isinstance(seller, dict):
            product_info["seller"] = seller.get("name", "")
        else:
            product_info["seller"] = seller

    aggregate_rating = product_data.get("aggregateRating")
    if aggregate_rating and isinstance(aggregate_rating, dict):
        product_info["ratingValue"] = aggregate_rating.get("ratingValue", "")
        product_info["ratingCount"] = aggregate_rating.get("ratingCount", "")

    return product_info

async def fetch_and_extract(url, session, semaphore):
    async with semaphore:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    print(f"Error accessing {url}: Status {response.status}")
                    return None
                text = await response.text()
                return extract_product_schema_from_text(url, text)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

async def scrape_products(sitemap_url, scrape_limit=float('inf'), sample_size=5, max_concurrent=20):
    async with aiohttp.ClientSession() as session:
        urls = await extract_sitemap_urls(sitemap_url, session, check_products=True, sample_size=sample_size)
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

async def scrape_from_website(website_url: str, scrape_limit: int = 5, sample_size: int = 3, max_concurrent: int = 20):
    sitemap_urls = find_sitemaps(website_url)
    if sitemap_urls:
        first_sitemap = sitemap_urls[0]
        # Since we are now in an async context, use asyncio.run only if running standalone.
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
