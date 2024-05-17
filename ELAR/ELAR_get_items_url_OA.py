import requests
from bs4 import BeautifulSoup
import os
import numpy as np
import pandas as pd
import multiprocessing as mp
from multiprocessing import Pool
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import time
import ast
from urllib.error import HTTPError

def find_files_url(url):
    session = requests.Session()
    retryer = Retry(total=5, read=5, connect=5, status=1, redirect=1, status_forcelist=None) 
    adapter = HTTPAdapter(max_retries=retryer)
    adapter.max_retries.respect_retry_after_header = False
    try:
        # Send a GET request to the URL
        response = session.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the specific div containing the href
        archive_name_divs = soup.find_all('div', class_='archive_name col0')
        hrefs = []
        if archive_name_divs:
            for archive_name_div in archive_name_divs:
                a_tag = archive_name_div.find('a', class_='new-primary new-primary-tint-hover multiline')
                if a_tag and 'href' in a_tag.attrs:
                    hrefs.append(a_tag['href'])
                    print(hrefs)
            return hrefs
        return None 
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        time.sleep(0.5)#it was 0.5 when levi did it
        session.close()
        return None
    
def apply_fetch_urls(url):
    return find_files_url(url)

def parallelize_dataframe_and_save(df, func, n_cores=mp.cpu_count()):
    results = []
    partial_results = []
    pool = mp.Pool(n_cores)
    for i, result in enumerate(pool.imap(func, df['URL']), 1):
        results.append(result)
        partial_results.append(result)
        # Save results every 10 rows
        if i % 50 == 0:
            save_partial_results(df, partial_results, i)
            partial_results = []  # Reset the partial results after saving
    
    pool.close()
    pool.join()

    if partial_results:
        save_to_csv(partial_results, 'results_file_url_final.csv')

    df['File_URLs'] = results

    return df

def save_partial_results(df, partial_results, identifier):
    # Add the partial results to the DataFrame and save
    partial_results_df = df.iloc[:len(partial_results)].copy()
    partial_results_df['File_URLs'] = partial_results
    save_to_csv(partial_results_df, f'results_file_url_partial_{identifier}.csv')

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

if __name__ == "__main__":

    
    items = pd.read_csv('final_results.csv')

    OA_items = items[items['Access Level'] == 'O_OpenAccess']
    print(len(OA_items))

    all_results_df = parallelize_dataframe_and_save(OA_items, apply_fetch_urls)
    save_to_csv(all_results_df, 'full_results_with_urls.csv')
