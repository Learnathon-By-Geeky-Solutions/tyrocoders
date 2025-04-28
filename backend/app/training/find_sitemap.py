import requests
from bs4 import BeautifulSoup
import re
import itertools
SITE_MAP_LITERAL = "sitemap_index.xml"
# List of common sitemap names
common_sitemaps = [
    "sitemap.xml", SITE_MAP_LITERAL, "sitemap.xml.gz", "sitemap_index.xml.gz",
    "sitemap.html", "sitemap.php", "feeds/posts/default?orderby=updated",
    "sitemap_index.html", "sitemap_index", "sitemap-index.xml", SITE_MAP_LITERAL
]

def find_sitemap_in_robots(website):
    """Check if sitemap is listed in robots.txt."""
    robots_url = website.rstrip('/') + '/robots.txt'
    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            # Search for "Sitemap" directive in the robots.txt
            for line in response.text.splitlines():
                if line.lower().startswith('sitemap:'):
                    return line.split(':', 1)[1].strip()
    except requests.RequestException:
        return None
    return None

def check_sitemap_location(website):
    """Brute-force common sitemap names and locations."""
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
    """Extract additional sitemaps if the URL is a sitemap index (XML)."""
    try:
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            sitemaps = []
            for loc in soup.find_all('loc'):
                sitemaps.append(loc.text)
            return sitemaps
    except requests.RequestException:
        return []
    return []

def find_all_sitemaps(website):
    """Find all sitemaps for the domain and its subdomains."""
    sitemaps = []

    # First, check robots.txt for sitemap URLs
    robots_sitemap = find_sitemap_in_robots(website)
    if robots_sitemap:
        print(f"Found sitemap in robots.txt: {robots_sitemap}")
        sitemaps.append(robots_sitemap)

    # Second, try brute-forcing common sitemap names and locations
    if not robots_sitemap:
        sitemap = check_sitemap_location(website)
        if sitemap:
            sitemaps.append(sitemap)

    # If it's an index sitemap, recursively find other sitemaps
    all_sitemaps = []
    for sitemap in sitemaps:
        all_sitemaps.append(sitemap)
        if sitemap.endswith(SITE_MAP_LITERAL) or sitemap.endswith("sitemap_index.xml.gz"):
            additional_sitemaps = extract_sitemaps_from_xml(sitemap)
            if additional_sitemaps:
                all_sitemaps.extend(additional_sitemaps)

    return sitemaps

def find_sitemaps_for_subdomains(website):
    """Find sitemaps for subdomains of the website."""
    # subdomains = []  # Add subdomains manually or use a subdomain discovery tool
    # For simplicity, let's assume we're just checking a few subdomains
    subdomains_to_check = [f"www.{website}", f"blog.{website}", f"shop.{website}"]

    all_sitemaps = []
    for subdomain in subdomains_to_check:
        sitemaps = find_all_sitemaps(subdomain)
        all_sitemaps.extend(sitemaps)

    return all_sitemaps

# Main function to find sitemaps for the domain and subdomains
def find_sitemaps(website):
    # First, find sitemaps for the main domain
    print(f"Finding sitemaps for {website}")
    domain_sitemaps = find_all_sitemaps(website)

    # Then, find sitemaps for subdomains
    subdomain_sitemaps = find_sitemaps_for_subdomains(website)

    all_sitemaps = domain_sitemaps + subdomain_sitemaps
    print(f"Total sitemaps found: {len(all_sitemaps)}")
    return all_sitemaps

if __name__ == "__main__":
    website = "https://www.vibegaming.com.bd/"
    sitemaps = find_sitemaps(website)
    print(sitemaps)