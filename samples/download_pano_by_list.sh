#!/bin/bash

# Set the PYTHONPATH to include the current directory
export PYTHONPATH=.:$PYTHONPATH

# Define the base directory for the samples and scripts
# BASE_DIR="/path/to/geosys/directory" # Replace with the actual base directory
BASE_DIR=$(pwd)

# Config
# OUTPUT_DIR="$BASE_DIR/samples/data/$LOCATION_NAME"
OUTPUT_DIR="$BASE_DIR/../data/$LOCATION_NAME"
EXPAND_LEVEL=2
EXPAND_DIS=200
LOCATION_NAME="XinjiangTaZhiXiLu"
PID=02015800001407191122520306A

# Create the output directory if it does not exist
mkdir -p "$OUTPUT_DIR/cache"
mkdir -p "$OUTPUT_DIR/tmp"
mkdir -p "$OUTPUT_DIR/pano"

# Run the grab_line_pano_info.py script and store the output
echo "Gathering panorama information..."
python "$BASE_DIR/scripts/grab_line_pano_info.py" "$PID" -o "$OUTPUT_DIR" -l "$EXPAND_LEVEL" -d "$EXPAND_DIS" || {
    echo "Error: grab_line_pano_info.py failed."
    exit 1
}

# Check if the pids.txt file exists before proceeding
PID_FILE="$OUTPUT_DIR/tmp/pids.txt"
if [ ! -f "$PID_FILE" ]; then
    echo "Error: $PID_FILE not found."
    exit 1
fi

# Download the panoramas using the download_map_pano.py script
echo "Downloading panoramas..."
while IFS= read -r pid; do
    python "$BASE_DIR/scripts/download_map_pano.py" -t bmap "$pid" -o "$OUTPUT_DIR/pano" || {
        echo "Error: download_map_pano.py failed for PID $pid."
    }
done < "$PID_FILE"

echo "🍺Panorama download complete."
