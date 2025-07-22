import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
from multiprocessing import Pool, cpu_count

def fetch_details(row):
    language = row['Language']
    link = row['Link']
    url = f"{link}"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract number of speakers
    speakers_tag = soup.find('div', class_='block-extra-field-blocknodelanguage-profilelanguages-associated-language-speakers')
    speakers = speakers_tag.find('span', class_='field-content').text.strip() if speakers_tag else 'None'
    
    # Extract Glottocode
    glottocode_tag = soup.find('div', class_='field--name-field-glottocode')
    glottocode = glottocode_tag.find('div', class_='field__item').text.strip() if glottocode_tag else 'None'
    
    print(f"Processed language: {language}")
    return {'Language': language, 'Speakers': speakers, 'Glottocode': glottocode}

def scrape_language_details(input_csv):
    # Load the chunk DataFrame from the CSV file
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: File '{input_csv}' not found.")
        return
    
    # Process chunks in parallel
    with Pool(cpu_count()) as pool:
        results = pool.map(fetch_details, [row for index, row in df.iterrows()])
    
    # Create additional DataFrame from results
    additional_df = pd.DataFrame(results)
    
    # Merge with original DataFrame
    result_df = pd.merge(df, additional_df, on='Language', how='left')
    
    # Save the final DataFrame to a CSV file
    output_csv = f'{input_csv.split(".csv")[0]}_details.csv'
    result_df.to_csv(output_csv, index=False)
    
    print(f"Processed chunk saved to {output_csv}")

if __name__ == "__main__":
    # Check if the CSV file path is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python unesco.py <path_to_chunk_csv>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    
    # Process the chunk and save the result
    scrape_language_details(input_csv)
