import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import ast
import multiprocessing as mp
from multiprocessing import Pool
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

#started v slow, continued a lil faster? guess depends on internet.. 

def fetch_url_data(url_list):
    content_lengths = []
    content_dispositions = []
    session = requests.Session()
    retryer = Retry(total=5, read=5, connect=5, status=1, redirect=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retryer)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    for url in url_list:
        transformed_url = url.replace("https://eldp.access.preservica.com/uncategorized/", "https://www.elararchive.org/download/file/")
        try:
            response = session.get(transformed_url)
            response.raise_for_status()
            content_lengths.append(len(response.content))
            print(len(response.content))
            content_dispositions.append(response.headers.get('Content-Disposition', ''))
        except requests.RequestException as e:
            print(f"Request failed for {transformed_url}: {e}")
            content_lengths.append(None)
            content_dispositions.append(None)
    
    session.close()
    return content_lengths, content_dispositions
    
# Function to apply to each row
def process_row(url_list):
    return fetch_url_data(url_list)

# Parallelize the process and save results every 50 rows
def parallelize_dataframe_and_save(df, func, n_cores=mp.cpu_count()):
    results = []
    partial_results = []
    pool = mp.Pool(n_cores)

    for i, result in enumerate(pool.imap(func, df['File_URLs']), 1):
        results.append(result)
        partial_results.append(result)
        
        # Save results every 50 rows
        if i % 50 == 0:
            content_lengths, content_dispositions = zip(*partial_results)
            df_partial = pd.DataFrame({
                'File_URLs': df['File_URLs'][:i],
                'Content_Lengths': content_lengths,
                'Content_Dispositions': content_dispositions
            })
            df_partial.to_csv(f'results_length_partial_{i}.csv', index=False)
            partial_results = []  # Reset the partial results after saving

    pool.close()
    pool.join()

    if partial_results:
        content_lengths, content_dispositions = zip(*partial_results)
        df_partial = pd.DataFrame({
            'URL_List': df['URL_List'][:len(results)],
            'Content_Lengths': content_lengths,
            'Content_Dispositions': content_dispositions
        })
        df_partial.to_csv('results_length_final.csv', index=False)

    return results

if __name__ == "__main__":

    df = pd.read_csv('results_file_url_partial_9100.csv') 
    df['File_URLs'] = df['File_URLs'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    all_results = parallelize_dataframe_and_save(df, process_row)

    # Combine results into a final DataFrame
    content_lengths, content_dispositions = zip(*all_results)
    df['Content_Lengths'] = content_lengths
    df['Content_Dispositions'] = content_dispositions

    # Save the final DataFrame
    df.to_csv('final_results_length_url.csv', index=False)

    print(df)

