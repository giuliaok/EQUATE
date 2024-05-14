#!/bin/bash

# Define the path to your Python script
python_script="ailla_dataset_creation.py"

# Define the folder containing the pickled files
folder_path="AILLA_sub_data"

# Get a list of all pickled files in the folder
pickled_files=($folder_path/*.pkl)

# Loop through each pickled file and run the Python script
for file in "${pickled_files[@]}"; do
    echo "Processing $file"
    python3 "$python_script" "$file"
    echo "Finished processing $file"
    sleep 10
done
