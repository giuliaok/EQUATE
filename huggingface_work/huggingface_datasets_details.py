import requests
import pandas as pd
from bs4 import BeautifulSoup
from queue import Queue
import multiprocessing
from itertools import product
import json
from multiprocessing import Pool
import time

def extract_huggingface_languages(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    # Initialize lists to store extracted data
    languages = []
    iso_codes = []
    datasets_links = []
    models_links = []
    datasets_numbers = []
    model_numbers = []

    # Extract data from each row of the table
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 0:  # Ensure it's not the header row
            language = cols[0].get_text(strip=True)
            iso_code = cols[1].find('code').get_text(strip=True)
            datasets_link = "https://huggingface.co" + cols[2].find('a')['href']
            models_link = "https://huggingface.co" + cols[3].find('a')['href']
            datasets_number = int(cols[2].find('a').get_text(strip=True).replace(',', ''))
            model_number = int(cols[3].find('a').get_text(strip=True).replace(',', ''))
            
            # Append data to lists
            languages.append(language)
            iso_codes.append(iso_code)
            datasets_links.append(datasets_link)
            models_links.append(models_link)
            datasets_numbers.append(datasets_number)
            model_numbers.append(model_number)

    # Create DataFrame
    df = pd.DataFrame({
        'Language': languages,
        'ISO Code': iso_codes,
        'Datasets Link': datasets_links,
        'Models Link': models_links,
        'Datasets Number': datasets_numbers,
        'Model Number': model_numbers
    })
    return df

def extract_huggingface_tasks(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    a_elements = soup.find_all('a', class_='mb-1 mr-1 md:mb-1.5 md:mr-1.5 rounded-lg')

    # Extract href attributes from the <a> elements
    hrefs = [a['href'] for a in a_elements]
    for i in range(len(hrefs)):
        hrefs[i] = hrefs[i].replace("/datasets?task_categories=task_categories%3A", "")
    
    return hrefs 


def get_datasets_json(task_categories, language, page=None):
    scheme = "https"
    host = "huggingface.co"
    filename = "/datasets-json"

    # Query parameters
    query_params = {
        "task_categories": f"task_categories:{task_categories}",
        "language": f"language:{language}",
        "sort": "trending"
    }
    if page is not None:
        query_params["p"] = page

    # Construct the full URL
    url = f"{scheme}://{host}{filename}"

    # Send GET request with query parameters
    with requests.Session() as session:
        response = requests.get(url, params=query_params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse JSON response and return it
            return response.json()
        else:
            # Print error message if request failed
            print("Failed to retrieve data. Status code:", response.status_code)
            time.sleep(0.5)
            session.close()
            return None 

def get_data_for_combinations(languages, pipeline_tags):
    # Initialize an empty list to store the results
    results = []

    # Iterate over each language and pipeline tag combination
    for language in languages:
        for pipeline_tag in pipeline_tags:
            page = None
            while True:
                print(f"Processing language '{language}' and pipeline tag '{pipeline_tag}'...")
                # Call the get_models_json function for the current combination and page
                response_data = get_datasets_json(pipeline_tag, language, page=page)
                if response_data:
                    # Append the results to the list
                    results.append({"language": language, "pipeline_tag": pipeline_tag, "response": response_data})
                    # Check if there are more pages
                    if len(response_data['datasets']) == 30:
                        page = 1 if page is None else page + 1
                        print(page)
                    else:
                        break
                else:
                    break  # Exit loop if there's an error

    # Create a DataFrame from the results list
    df = pd.DataFrame(results)

    return df

def process_row(row):
    language = row['Language']
    pipeline_tag = row['Pipeline_Tag']
    return get_data_for_combinations([language], [pipeline_tag])

def parallelize_dataframe_processing(df, process_row, num_processes=multiprocessing.cpu_count()):

    # Create a pool of worker processes
    pool = Pool(processes=num_processes)

    # Apply the function to each row of the DataFrame in parallel
    result_df_list = pool.map(process_row, [row for index, row in df.iterrows()])

    # Concatenate the resulting DataFrames
    final_df = pd.concat(result_df_list, ignore_index=True)

    # Close the pool
    pool.close()
    pool.join()

    return final_df

if __name__ == "__main__":


    df = extract_huggingface_languages('https://huggingface.co/languages')
    tasks = extract_huggingface_tasks('https://huggingface.co/datasets?sort=trending')

    languages = df['ISO Code'].to_list()
    # Define lists of languages and pipeline tags
    combinations = list(product(languages, tasks))

    df = pd.DataFrame(combinations, columns=["Language", "Pipeline_Tag"])

    final_df = parallelize_dataframe_processing(df, process_row)
 
    final_df.to_csv('huggingface_datasets.csv') 
     #result_df = get_data_for_combinations(languages, tasks)
    #result_df['datasets_count'] = result_df['response'].apply(lambda x: len(x['datasets']))
    #result_df['sum'] = result_df.groupby(['language', 'pipeline_tag'])['datasets_count'].transform('sum')
    #df = result_df.drop_duplicates(subset=['language', 'pipeline_tag'])
