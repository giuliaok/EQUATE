#!/bin/bash

# Define directories
INPUT_DIR="HF_time_series_split"
OUTPUT_DIR="HF_time_series_results"
PROCESSED_DIR="HF_time_series_processed"
PYTHON_SCRIPT="commits_explorer_timely.py"

# Process each file in the input directory
for file in "$INPUT_DIR"/*.csv; do
    if [ -f "$file" ]; then
        echo "Processing file: $file"
        python3 "$PYTHON_SCRIPT" "$file" "$OUTPUT_DIR"
        mv "$file" "$PROCESSED_DIR/"
        echo "Moved $file to $PROCESSED_DIR"
        echo "Waiting for 30 seconds before processing the next file..."
        sleep 30
    fi
done