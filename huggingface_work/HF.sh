#!/bin/bash

# Define the folder containing the CSV files
input_folder="/Users/go202/Desktop/EQUATE/huggingface_work/split_HF"
output_folder="/Users/go202/Desktop/EQUATE/huggingface_work/split_HF_results"
python_script="/Users/go202/Desktop/EQUATE/huggingface_work/huggingface_datasets_details.py"


# Iterate over each CSV file in the input folder
for csv_file in "$input_folder"/*.csv; do
    # Get the base name of the file (without path)
    base_name=$(basename "$csv_file" .csv)
    
    # Define the output file name
    output_file="$output_folder/${base_name}_processed.csv"
    
    # Run the Python script to process the CSV file
    python "$python_script" "$csv_file" "$output_file"
    
    # Wait for a minute before processing the next file
    echo "Done. Waiting for a minute before processing the next file..."
    sleep 60
    # Print the name of the file being processed
    echo "Processing file: $csv_file"
done
