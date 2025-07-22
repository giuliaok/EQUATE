import requests
from bs4 import BeautifulSoup
import os
import numpy as np
import pandas as pd
import multiprocessing as mp
from multiprocessing import Pool
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import pickle
import ast
from urllib.error import HTTPError

def fetch_urls_access(base_url):
    urls = []
    page_number = 1
    while True:
        url = f"{base_url}?pg={page_number}"
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='one_sixth grey_block new-secondary-background result-item')
            if not divs:
                break
            for div in divs:
                a_tag = div.find('a', class_='new-primary new-primary-tint-hover multiline')
                access_level_tag = div.find('div', class_='archive_data_content col2')
                if a_tag and access_level_tag:
                    title = a_tag.text.strip()
                    href = a_tag['href']
                    access_level = access_level_tag.find('p').text.strip()
                    
                    # Extract language name and code from the HTML content
                    html_content = response.content
                    language_soup = BeautifulSoup(html_content, 'html.parser')
                    language_name_tag = language_soup.find('span', class_='metadata-title', text='Name')
                    language_name = language_name_tag.find_next('span', class_='metadata-content').text if language_name_tag else None
                    language_code_tag = language_soup.find('span', class_='metadata-title', text='Code')
                    language_code = language_code_tag.find_next('span', class_='metadata-content').text if language_code_tag else None
                    
                    # Append the extracted information to the urls list
                    urls.append((title, href, access_level, language_name, language_code))
                    print('done')
                    
            page_number += 1
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            break
    return urls

def apply_fetch_urls_access(url):
    return fetch_urls_access(url)

def parallelize_dataframe_and_save(df, func, n_cores=mp.cpu_count()):
    results = []
    partial_results = []
    pool = mp.Pool(n_cores)
    for i, result in enumerate(pool.imap(func, df['url_collection']), 1):
        results.append(result)
        partial_results.append(result)
        # Save results every 10 rows
        if i % 10 == 0:
            flat_results = [item for sublist in partial_results for item in sublist]
            save_to_csv(flat_results, f'results_partial_{i}.csv')
            partial_results = []  # Reset the partial results after saving
    pool.close()
    pool.join()
    return results

def save_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['Title', 'URL', 'Access Level', 'Language Name', 'Language Code'])
    df.to_csv(filename, index=False)


if __name__ == "__main__":
     
    collection = pd.read_csv('ELAR_catalogue.csv')

    all_results = parallelize_dataframe_and_save(collection, apply_fetch_urls_access)

    combined_results = [item for sublist in all_results for item in sublist]
    save_to_csv(combined_results, 'final_results.csv')

    # Print the final DataFrame
    final_df = pd.DataFrame(combined_results, columns=['Title', 'URL', 'Access Level', 'Language Name', 'Language Code'])
    print(final_df)

    

  