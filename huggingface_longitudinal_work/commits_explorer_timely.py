import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
from multiprocessing import Pool, cpu_count
import time

REQUEST_COUNT = 0
REQUEST_LIMIT = 30  # Requests before pausing; higher values tend to trigger rate limiting.
SLEEP_TIME = 20


def make_request(url):
    global REQUEST_COUNT
    if REQUEST_COUNT >= REQUEST_LIMIT:
        print(f"Rate limit reached; pausing for {SLEEP_TIME} seconds.")
        time.sleep(SLEEP_TIME)
        REQUEST_COUNT = 0
    response = requests.get(url)
    REQUEST_COUNT += 1
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return None
    return response.text


def find_huggingface_datasets(dataset_url, df=None):
    if df is None:
        df = pd.DataFrame(columns=['dataset', 'dataset_url'])
    dataset_request = make_request(dataset_url)
    if dataset_request is None:
        return df['dataset_url'].tolist()
    dataset_soup = BeautifulSoup(dataset_request, 'html.parser')
    articles_data = []
    articles = dataset_soup.find_all('article')
    if articles:
        for article in articles:
            text = article.h4.text.strip() if article.h4 else ''
            href = article.a['href'] if article.a else ''
            articles_data.append({'dataset': text, 'dataset_url': href})

    temp_df = pd.DataFrame(articles_data)
    df = pd.concat([df, temp_df], ignore_index=True)

    sections = dataset_soup.find_all('section')
    if sections:
        nav = sections[-1].find('nav')
        if nav:
            next_page_link = nav.find_all('a')[-1].get('href')
            if next_page_link:
                next_page_url = f'https://huggingface.co/datasets{next_page_link}'
                return find_huggingface_datasets(next_page_url, df)
    
    return df['dataset_url'].tolist()

def find_earliest_commit(model_name):
    request_text = make_request(f'https://huggingface.co{model_name}')
    if request_text is None:
        return None
    soup = BeautifulSoup(request_text, 'html.parser')
    hrefs = [a['href'] for a in soup.find_all('a', class_='tab-alternate')]
    commits_href = ['https://huggingface.co' + url for url in hrefs if '/tree/main' in url]
    if commits_href:
        commits_href_history = commits_href[0].replace('tree', 'commits')
        commits_request_text = make_request(commits_href_history)
        if commits_request_text is None:
            return None
        commits_soup = BeautifulSoup(make_request(commits_href_history), 'html.parser')
        time_elements = commits_soup.find_all('time')
        datetimes = [time['datetime'] for time in time_elements]
        processed_datetime = [datetime.fromisoformat(dt_str) for dt_str in datetimes]
        if processed_datetime:
            return min(processed_datetime)
    return None

def find_earliest_datetime_pls(lst):
    datetimes = [item for item in lst if isinstance(item, datetime)]
    earliest_datetime = min(datetimes) if datetimes else None
    return earliest_datetime

def process_dataset_url(url):
    dataset_urls = find_huggingface_datasets(url)
    return dataset_urls

def process_model_name(model_name):
    return find_earliest_commit(model_name)

def parallel_process_datasets(dataset_urls):
    with Pool(cpu_count()) as pool:
        all_datasets = pool.map(process_dataset_url, dataset_urls)
    return all_datasets

def parallel_process_commits(model_names):
    with Pool(cpu_count()) as pool:
        earliest_updates = pool.map(process_model_name, model_names)
    return earliest_updates

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    df = pd.read_csv(input_file)
    print(df)

    # Parallelize dataset URL processing
    all_datasets = parallel_process_datasets(df['Datasets Link'])
    df['all_datasets'] = all_datasets

    # Flatten the list of all datasets
    flattened_datasets = [item for sublist in df['all_datasets'] for item in sublist]

    # Parallelize commit history processing
    earliest_updates = parallel_process_commits(flattened_datasets)
    df['earliest_update'] = df['all_datasets'].apply(lambda x: [find_earliest_commit(item) for item in x])
    df['earliest_datetime'] = df['earliest_update'].apply(find_earliest_datetime_pls)

    output_file = os.path.join(output_dir, os.path.basename(input_file))
    df.to_csv(output_file, index=False)
