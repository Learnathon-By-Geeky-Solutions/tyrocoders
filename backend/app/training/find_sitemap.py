"""
sitemap_finder.py

This module provides utilities to discover sitemap files for a given website and its common subdomains.
It uses several strategies to locate sitemaps, including:
- Parsing `robots.txt`
- Brute-forcing common sitemap URLs
- Extracting child sitemaps from sitemap index files

The goal is to comprehensively enumerate all publicly accessible sitemaps associated with a domain.

Functions:
- find_sitemap_in_robots(website): Check if a sitemap is declared in the site's robots.txt file.
- check_sitemap_location(website): Brute-force common sitemap URLs to find existing sitemap files.
- extract_sitemaps_from_xml(sitemap_url): If the sitemap is an index, extract sub-sitemaps from it.
- find_all_sitemaps(website): Combines all methods to gather sitemaps for the main domain.
- find_sitemaps_for_subdomains(website): Attempts to locate sitemaps for typical subdomains.
- find_sitemaps(website): Aggregates all sitemaps for a website and its subdomains.
"""

import requests
from bs4 import BeautifulSoup

SITE_MAP_LITERAL = "sitemap_index.xml"

# List of common sitemap filenames and formats
common_sitemaps = [
    "sitemap.xml", SITE_MAP_LITERAL, "sitemap.xml.gz", "sitemap_index.xml.gz",
    "sitemap.html", "sitemap.php", "feeds/posts/default?orderby=updated",
    "sitemap_index.html", "sitemap_index", "sitemap-index.xml", SITE_MAP_LITERAL
]

def find_sitemap_in_robots(website):
    """
    Check if the sitemap URL is listed in the robots.txt file of the website.

    Args:
        website (str): The base URL of the website (e.g., https://example.com)

    Returns:
        str or None: The sitemap URL if found, otherwise None
    """
    robots_url = website.rstrip('/') + '/robots.txt'
    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.lower().startswith('sitemap:'):
                    return line.split(':', 1)[1].strip()
    except requests.RequestException:
        return None
    return None

def check_sitemap_location(website):
    """
    Try common sitemap URLs directly under the website root.

    Args:
        website (str): The base URL of the website.

    Returns:
        str or None: First valid sitemap URL found, or None if not found.
    """
    for sitemap in common_sitemaps:
        sitemap_url = f"{website.rstrip('/')}/{sitemap}"
        try:
            response = requests.get(sitemap_url)
            if response.status_code == 200:
                print(f"Found sitemap at: {sitemap_url}")
                return sitemap_url
        except requests.RequestException:
            continue
    return None

def extract_sitemaps_from_xml(sitemap_url):
    """
    Extract nested sitemaps from a sitemap index XML file.

    Args:
        sitemap_url (str): URL of the sitemap index.

    Returns:
        list[str]: List of nested sitemap URLs.
    """
    try:
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            return [loc.text for loc in soup.find_all('loc')]
    except requests.RequestException:
        return []
    return []

def find_all_sitemaps(website):
    """
    Discover all relevant sitemaps for a given website.

    Combines methods:
    - robots.txt inspection
    - common filename brute-forcing
    - sitemap index expansion

    Args:
        website (str): Website URL.

    Returns:
        list[str]: List of sitemap URLs discovered.
    """
    sitemaps = []

    # Step 1: robots.txt
    robots_sitemap = find_sitemap_in_robots(website)
    if robots_sitemap:
        print(f"Found sitemap in robots.txt: {robots_sitemap}")
        sitemaps.append(robots_sitemap)

    # Step 2: common paths
    if not robots_sitemap:
        sitemap = check_sitemap_location(website)
        if sitemap:
            sitemaps.append(sitemap)

    # Step 3: extract from sitemap index
    all_sitemaps = []
    for sitemap in sitemaps:
        all_sitemaps.append(sitemap)
        if sitemap.endswith(SITE_MAP_LITERAL) or sitemap.endswith("sitemap_index.xml.gz"):
            additional_sitemaps = extract_sitemaps_from_xml(sitemap)
            if additional_sitemaps:
                all_sitemaps.extend(additional_sitemaps)

    return all_sitemaps

def find_sitemaps_for_subdomains(website):
    """
    Check typical subdomains for sitemaps (e.g., www, blog, shop).

    Args:
        website (str): Base domain name (without subdomain prefix).

    Returns:
        list[str]: List of discovered sitemaps from subdomains.
    """
    subdomains_to_check = [f"https://www.{website}", f"https://blog.{website}", f"https://shop.{website}"]
    all_sitemaps = []
    for subdomain in subdomains_to_check:
        sitemaps = find_all_sitemaps(subdomain)
        all_sitemaps.extend(sitemaps)
    return all_sitemaps

def find_sitemaps(website):
    """
    Aggregate all sitemaps found for a given domain and its subdomains.

    Args:
        website (str): Full website URL, including protocol (e.g., https://example.com)

    Returns:
        list[str]: All sitemap URLs found.
    """
    print(f"Finding sitemaps for {website}")
    domain_sitemaps = find_all_sitemaps(website)
    subdomain_sitemaps = find_sitemaps_for_subdomains(website)
    all_sitemaps = domain_sitemaps + subdomain_sitemaps
    print(f"Total sitemaps found: {len(all_sitemaps)}")
    return all_sitemaps

if __name__ == "__main__":
    website = "https://www.vibegaming.com.bd/"
    sitemaps = find_sitemaps(website)
    print(sitemaps)