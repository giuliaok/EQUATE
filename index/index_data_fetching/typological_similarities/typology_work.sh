#!/bin/bash

# Configurations
chunks_folder="chunks"
processed_folder="processed"
input_file="main_dataset.csv"
chunk_size=1000  # Adjust based on your data size

# Create necessary folders
mkdir -p "$chunks_folder"
mkdir -p "$processed_folder"

# Split the dataset into chunks
echo "📊 Splitting dataset into chunks of $chunk_size rows..."
tail -n +2 "$input_file" | split -l $chunk_size - "$chunks_folder/chunk_"
for chunk in "$chunks_folder"/chunk_*; do
    header=$(head -n 1 "$input_file")
    (echo "$header"; cat "$chunk") > "${chunk}.csv"
    rm "$chunk"
done
echo "✅ Dataset split into chunks."

# Process each chunk in parallel
echo "🚀 Processing chunks in parallel..."
find "$chunks_folder" -name "chunk_*.csv" | parallel -j 4 python unesco.py {}

# Move processed files to the results folder
echo "📂 Moving processed files to $processed_folder..."
for chunk_file in "$chunks_folder"/chunk_*_details.csv; do
    mv "$chunk_file" "$processed_folder/"
done

echo "✅ All chunks processed and saved in $processed_folder."
