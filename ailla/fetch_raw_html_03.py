import requests
import os
from time import sleep
import random
def save_html(html_content, file_name):
    """Save the HTML content to a file."""
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(html_content)

def fetch_html(url, retries=3, timeout=5000):
    """Fetch HTML content for a given URL with retries."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        if retries > 0:
            print(f"Retry {retries} for {url} due to {str(e)}")
            sleep(2)  # Wait for 2 seconds before retrying
            return fetch_html(url, retries - 1, timeout)
        else:
            print(f"Failed to fetch {url} after retries: {str(e)}")
            return None

def crawl_site(base_url, start_id, end_id):
    """Crawl the website from start_id to end_id."""
    for set_id in range(start_id, end_id):
        file_name = f"set_{set_id}.html"
        if os.path.exists(file_name):
#             print(f"{file_name} already exists. Skipping download.")
            continue
        else:
            print(f"{file_name} downloading.")
        url = f"{base_url}/{set_id}/"
        print(f"Fetching {url}")
        html_content = fetch_html(url)
        if html_content:
            save_html(html_content, file_name)
        sleep(random.uniform(1, 2))



base_url = "https://www.ailla.utexas.org/sets"
start_id = 4000
end_id = 5000
crawl_site(base_url, start_id, end_id)
