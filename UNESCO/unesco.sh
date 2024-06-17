#!/bin/bash

# Paths
chunks_folder="/Users/go202/Desktop/EQUATE/UNESCO/unesco_chunks"
processed_folder="/Users/go202/Desktop/EQUATE/UNESCO/processed_unesco"

# Create processed files folder if it doesn't exist
mkdir -p "$processed_folder"

# Iterate over each chunk
for chunk_file in "$chunks_folder"/*.csv; do
    chunk_filename=$(basename "$chunk_file")
    
    # Run Python script to process the chunk
    python unesco.py "$chunk_file"
    
    # Move processed file to results folder
    mv "${chunk_file%.csv}_details.csv" "$processed_folder/"
done

echo "All chunks processed."