import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urldefrag
import sys
import time

# Base URL for numpy documentation
BASE_URL = "https://pandas.pydata.org/docs/reference/"

def get_reachable_from_base_link(base_url):
    """
    Get all the links reachable from the base URL.

    Args:
        base_url (str): The base URL to start crawling from.

    Returns:
        set: A set of links reachable from the base URL.
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to fetch {base_url}: {e}")

    soup = BeautifulSoup(response.text, "html.parser")

    links = set()
    for a_tag in soup.find_all("a", href=True):
        link = a_tag["href"]
        full_url = urljoin(base_url, link)
        links.add(full_url)

    return links

def fetch_page_warnings(url):
    """
    Fetches warning messages from a given URL.

    This function attempts to retrieve the content of the specified URL and
    extract warning messages contained within <div class="admonition warning">
    elements. If the initial URL request fails, it tries to fetch the content
    from a modified URL by adding "generated/" after the base URL.

    Args:
        url (str): The URL of the page to fetch warnings from.

    Returns:
        tuple: A tuple containing:
            - list: A list of warning messages found on the page.
            - str or None: The modified URL if the initial request failed and
            the modified URL was used, otherwise None.
    """
    print(f"Fetching warnings from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for <article class="bd-article">
    article = soup.find("article", class_="bd-article")
    if not article:
        print(f"No <article class='bd-article'> found in {url}")
        return []

    # Extract warnings from the <div class="admonition warning">
    warnings = []
    for warning_div in soup.find_all("div", class_="admonition warning"):
        warning_text = warning_div.get_text(separator=" ", strip=True)
        warnings.append(warning_text)

    if warnings:
        print(f"Found {len(warnings)} warning(s) on {url}")
        time.sleep(2)
    else:
        print(f"No warnings found on {url}")

    return warnings


# Function to crawl pages starting from a base URL and search for warnings
def crawl_pandas_warnings(base_url, urls_to_visit=None, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()
    if urls_to_visit is None:
        urls_to_visit = set(base_url)

    warnings_dict = {}

    while urls_to_visit:
        print(f"URLs to visit: {len(urls_to_visit)}")
        current_url = urls_to_visit.pop()

        if current_url in visited_urls:
            continue

        print(f"Visiting {current_url}")
        visited_urls.add(current_url)

        # Fetch and extract warnings from the current page
        warnings = fetch_page_warnings(current_url)

        if warnings:
            warnings_dict[current_url] = warnings

        # Otherwise, parse the current page to find links to other numpy docs pages
        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {current_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            # This should be the links to other numpy documentation pages
            if a_tag.get("class", []) == ["reference", "internal"]:
                link = a_tag["href"]

                # Skip fragment links (anchors starting with #)
                if link.startswith("#") or "c-api" in link:
                    continue

                # Build the full URL
                full_url = urljoin(base_url, link)

                # Remove fragment part of the URL (e.g., `#section`)
                full_url, _ = urldefrag(full_url)

                # Only add links starting with the base URL and not already visited
                if full_url not in visited_urls and full_url.startswith(BASE_URL):
                    urls_to_visit.add(full_url)
                    print(f"Adding {full_url} to the list of URLs to visit")
    return warnings_dict


# First, crawl only the links directly reachable
# from the base url in the section <section id="python-api">
# this is done to ignore other sections such as c-api, other topics
# and acknowledgements
reachable_links = get_reachable_from_base_link(BASE_URL)

# Crawl all the pages reachable from the python-api section's links
# and look for warnings
warnings_from_pandas_doc = crawl_pandas_warnings(
    BASE_URL, urls_to_visit=reachable_links
)

##### WARNING RESEARCH FINISHED #####
for url, warning_list in warnings_from_pandas_doc.items():
    print(f"Warnings found on {url}:")
    for warning in warning_list:
        print(f"- {warning}")


# Dump warnings into json file
with open("pandas_warnings.json", "w") as f:
    json.dump(warnings_from_pandas_doc, f, indent=4)
