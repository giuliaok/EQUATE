import requests
from time import sleep


def save_html(html_content, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(html_content)


def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        print(response)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {str(e)}")
        return None


def crawl_site(base_url, start_id, end_id):
    for set_id in range(start_id, end_id + 1):
        print(set_id)
        url = f"{base_url}/{set_id}/"
        print(f"Fetching {url}")
        html_content = fetch_html(url)
        if html_content:
            save_html(html_content, f"set_{set_id}.html")
        sleep(1)  # Sleep for 1 second between requests to be polite


base_url = "https://www.ailla.utexas.org/sets"
start_id = 4000
end_id = 5000
crawl_site(base_url, start_id, end_id)
