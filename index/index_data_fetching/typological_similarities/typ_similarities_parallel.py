import pandas as pd
import logging
import sys
import os
from urielplus import urielplus

# Configure logging
logging.basicConfig(level=logging.INFO)

def calculate_typological_distance(df, u):
    """
    Calculate typological distance for each glottocode based on the 'model_n' column,
    handling errors and preventing sys.exit from terminating the script.
    """

    high_value_glottocodes = df.loc[df['model_n'] > 1000, 'glottocode'].tolist()
    high_value_languages = df.loc[df['model_n'] > 1000, 'name_left'].tolist()
    
    df['typological distance'] = None
    df['least_featural_distant_language'] = None
    
    for index, row in df.iterrows():
        current_glottocode = row['glottocode']
        min_row_distance = float('inf')
        least_distant_language = None
        
        for high_glottocode, high_language in zip(high_value_glottocodes, high_value_languages):
            try:
                distance = u.new_distance(["featural"], high_glottocode, current_glottocode)
            except SystemExit:
                logging.error(f"SystemExit caught while calculating distance between {high_glottocode} and {current_glottocode}. Assigning default distance of 1.")
                distance = 1
            except Exception as e:
                logging.error(f"Error calculating distance between {high_glottocode} and {current_glottocode}: {e}")
                distance = 1
            
            if distance < min_row_distance:
                min_row_distance = distance
                least_distant_language = high_language
        
        df.at[index, 'typological distance'] = min_row_distance
        df.at[index, 'least_featural_distant_language'] = least_distant_language
    
    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python typ_similarities_parallel.py <chunk_file>")
        sys.exit(1)
    
    chunk_file = sys.argv[1]
    output_file = os.path.splitext(chunk_file)[0] + "_details.csv"
    
    logging.info(f"📂 Processing chunk: {chunk_file}")


    df_chunk = pd.read_csv(chunk_file)
    df_chunk = calculate_typological_distance(df_chunk, u)
    
    # Save processed chunk
    df_chunk.to_csv(output_file, index=False)
    logging.info(f"✅ Processed chunk saved to: {output_file}")

    