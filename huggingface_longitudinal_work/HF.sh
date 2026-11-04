#!/bin/bash
# Batch-process HuggingFace language CSV chunks through huggingface_datasets_details.py.
#
# Usage:
#   DATA_DIR=/path/to/data ./HF.sh
#
# Expects:  $DATA_DIR/split_HF/*.csv          (input chunks)
# Produces: $DATA_DIR/split_HF_results/*.csv  (processed chunks)
#
# A short sleep between files keeps us under HuggingFace rate limits.
set -euo pipefail

# Directory this script lives in, so the Python helper is found regardless of CWD.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DATA_DIR="${DATA_DIR:-./data}"
input_folder="$DATA_DIR/split_HF"
output_folder="$DATA_DIR/split_HF_results"
python_script="$SCRIPT_DIR/huggingface_datasets_details.py"

mkdir -p "$output_folder"

for csv_file in "$input_folder"/*.csv; do
    base_name=$(basename "$csv_file" .csv)
    output_file="$output_folder/${base_name}_processed.csv"

    echo "Processing file: $csv_file"
    python "$python_script" "$csv_file" "$output_file"

    echo "Done. Waiting 60s before the next file to respect rate limits..."
    sleep 60
done
