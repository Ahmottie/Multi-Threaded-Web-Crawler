import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from time import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def process_page(url_depth):
    """
    This simply processes a webpage, extract links, and return them with the depth.0
    """
    url, depth = url_depth
    try:
        # Make an HTTP request to the URL
        response = requests.get(url, timeout=5)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Print the URL at the current depth
            print(f"At depth {depth}: {url}")

            # Extract links from the page and join them with the base URL
            links = [urljoin(url, link.get('href')) for link in soup.find_all('a')]
            return links, depth
    except Exception as e:
        print(f"Error processing {url}: {e}")

    return [], depth


def crawler(seed_url, max_pages=10, max_workers=12, executor_type=ProcessPoolExecutor):
    """
    Crawl web pages starting from a seed URL.
    """
    # Visited URLs
    visited = set()

    # Lock to ensure thread safety
    visited_lock = threading.Lock()

    # Queue to store URLs
    queue = deque([(seed_url, 0)])
    crawled_pages = 0
    all_links = []

    with executor_type(max_workers=max_workers) as executor:
        while queue and crawled_pages < max_pages:
            # Dequeue the next URL and its depth
            current_url, depth = queue.popleft()

            with visited_lock:
                if current_url in visited:
                    continue

                visited.add(current_url)

            # Process the current URL
            results = executor.map(process_page, [(link, depth + 1) for link in [current_url]])

            for links, new_depth in results:
                all_links.extend(links)
                queue.extend((link, new_depth) for link in links)

            crawled_pages += 1

    return all_links

if __name__ == "__main__":
    seed_url = "https://wikipedia.com"
    max_pages = 5

    s = time()
    result = crawler(seed_url, max_pages, max_workers=12)
    e = time()

    print(f"Time: {e - s}")
