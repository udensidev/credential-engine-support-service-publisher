import os
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import tldextract


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Function to get all links containing the user input domain from a given URL
"""def get_links_containing_domain(url, domain_string):
    
    Retrieves all links from a given URL that contain a specified domain string.

    This function sends a GET request to the specified URL, parses the HTML content to find all anchor tags, 
    and extracts the href attributes. It then filters the links to include only those that contain the specified domain string
    and are not mailto links. The filtered links are returned as a list.

    Parameters:
    url (str): The URL to retrieve and parse for links.
    domain_string (str): The domain string to filter the links.

    Returns:
    list: A list of links containing the specified domain string.

    Raises:
    requests.exceptions.RequestException: If an error occurs while making the GET request.
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            relevant_links = set()
            for link in links:
                href = link['href']
                full_url = urljoin(url, href)
                if domain_string in full_url and not full_url.startswith("mailto:"):
                    relevant_links.add(full_url)
            return list(relevant_links)
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing {url}: {e}")
        return []"""


"""def crawl_subdomains(subdomains, domain_string):
    
    Recursively crawls a list of subdomains and retrieves links containing a specified domain string.

    This function iterates over a list of subdomains, retrieves all links from each subdomain that
    contain the specified domain string, and aggregates the relevant links into a set to ensure uniqueness.
    The aggregated links are then returned as a list.

    Parameters:
    subdomains (list): A list of subdomains to crawl.
    domain_string (str): The domain string to filter the links.

    Returns:
    list: A list of unique links containing the specified domain string.

    Example:
    >>> subdomains = ["https://sub1.example.com", "https://sub2.example.com"]
    >>> domain_string = "example.com"
    >>> links = crawl_subdomains(subdomains, domain_string)
    >>> print(links)
    ['https://sub1.example.com/page1', 'https://sub2.example.com/page2']
    
    all_relevant_links = set()
    for subdomain in subdomains:
        print(f"Crawling subdomain: {subdomain} for links containing '{domain_string}'...")
        relevant_links = get_links_containing_domain(subdomain, domain_string)
        all_relevant_links.update(relevant_links)
    return list(all_relevant_links)"""

# Function to extract subdomains from a URL
def extract_subdomains(url):
    """
    Extracts subdomains from a given URL.

    This function uses the tldextract library to parse the given URL and extract the domain and subdomains.
    It constructs a list of subdomains in the format "sub.domain.suffix" and returns the original URL
    along with the constructed subdomain URLs.

    Parameters:
    url (str): The URL to extract subdomains from.

    Returns:
    list: A list containing the original URL and the constructed subdomain URLs.

    Example:
    >>> url = "https://sub.example.com"
    >>> subdomains = extract_subdomains(url)
    >>> print(subdomains)
    ['https://sub.example.com', 'https://sub.example.com']
    """
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}"  # e.g., "example.com"
    subdomains = [f"{sub}.{domain}" for sub in ext.subdomain.split('.')] if ext.subdomain else []
    return [url] + [f"https://{sub}" for sub in subdomains]

def crawl_and_filter_content(url, keywords, max_depth=2, visited=None, links_with_keywords=None):
    """
    Recursively crawls a website and filters content based on specified keywords.

    This function sends a GET request to the specified URL, parses the HTML content, and searches for the specified keywords. If any keywords are found, the URL and matched keywords are saved. The function then recursively crawls linked pages up to a specified depth, filtering content based on the same keywords.

    Parameters:
    url (str): The URL to start crawling from.
    keywords (list): A list of keywords to search for in the page content.
    max_depth (int, optional): The maximum depth to crawl. Default is 2.
    visited (set, optional): A set of URLs that have already been visited. Default is None.
    links_with_keywords (list, optional): A list to store URLs and matched keywords. Default is None.

    Returns:
    list: A list of dictionaries containing URLs and matched keywords.

    Raises:
    requests.RequestException: If an error occurs while making the GET request.

    Example:
    >>> url = "https://example.com"
    >>> keywords = ["support", "service"]
    >>> results = crawl_and_filter_content(url, keywords)
    >>> print(results)
    [{'url': 'https://example.com/page1', 'matched_keywords': ['support']}, {'url': 'https://example.com/page2', 'matched_keywords': ['service']}]
    """
    
    if visited is None and not isinstance(visited, set):
        visited = set()
    if links_with_keywords is None:
        links_with_keywords = []
    if url in visited or max_depth == 0:
        return links_with_keywords
    visited.add(url)
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return links_with_keywords
    except requests.RequestException:
        return links_with_keywords

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text().lower()
    matched_keywords = [keyword for keyword in keywords if keyword and keyword.lower() in page_text]
    if matched_keywords:
        
        links_with_keywords.append({
            'url': url,
            'matched_keywords': matched_keywords
        })
        save_relevant_links_to_json(links_with_keywords)
    #print("Relevant links and keywords saved to 'relevant_links.json'.")
    
    for link in soup.find_all('a', href=True):
        href = urljoin(url, link['href'])
        parsed_href = urlparse(href)
        if parsed_href.netloc.endswith(urlparse(url).netloc) and href not in visited:
            links_with_keywords = crawl_and_filter_content(href, keywords, max_depth - 1, visited, links_with_keywords)
    
    return links_with_keywords

# Function to scrape content from URLs
def scrape_page(url, file):
    """
    Scrapes the content from a given URL and writes it to a file.

    This function sends a GET request to the specified URL, parses the HTML content,
    extracts the text, and writes it to the provided file. The text content is separated by spaces
    and stripped of leading and trailing whitespace.

    Parameters:
    url (str): The URL to scrape content from.
    file (file object): The file object to write the scraped content to.

    Raises:
    requests.RequestException: If an error occurs while making the GET request.
    Exception: If an error occurs while parsing the HTML content or writing to the file.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True)
        file.write(page_text + "\n\n")
    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Save the relevant links and keywords to a JSON file
def save_relevant_links_to_json(data):
    """
    Saves the relevant links and keywords to a JSON file.

    This function takes a list of dictionaries containing URLs and matched keywords, and saves it to a JSON file named 'relevant_links.json' in the 'uploads' directory. The JSON data is formatted with an indentation of 2 spaces for readability.

    Parameters:
    data (list): A list of dictionaries containing URLs and matched keywords.
    """
    with open(os.path.join(BASE_DIR, 'uploads/relevant_links.json'), "w") as json_file:
        json.dump(data, json_file, indent=2)
    #print(f"Relevant links and keywords saved to 'relevant_links.json'.")


"""# Save the links to an Excel file
def save_links_to_excel(links, filepath):
    df = pd.DataFrame(links, columns=['Links'])
    df.to_excel(filepath, index=False)
    print(f"Links saved to 'links.xlsx'.")"""
