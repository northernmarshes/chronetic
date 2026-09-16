#!/usr/bin/env bash

# Create cache directory if it doesn't exist
mkdir -p .cache

# Function to check and copy a file
check_and_copy() {
  local file=$1
  local cache_md5=".cache/$(basename $file).md5"

  # Calculate current MD5
  current_md5=$(md5sum "$file" | cut -d' ' -f1)

  # Check if MD5 file exists and compare
  if [ ! -f "$cache_md5" ] || [ "$(cat $cache_md5)" != "$current_md5" ]; then
    echo "Changes detected in $file, copying to ESP32..."
    uv run mpremote cp "$file" ":$(basename $file)"
    echo "$current_md5" >"$cache_md5"
    echo "File $file copied successfully"
  else
    echo "No changes in $file"
  fi
}

# Process all Python files in front directory
for file in draw_utils.py font8x8.py epaper.py secrets.py; do
  if [ -f "src/$file" ]; then
    check_and_copy "src/$file"
  fi
done

# Process all data files in data directory
for file in src/data/*; do
  if [ -f "$file" ]; then
    check_and_copy "$file"
  fi
done

if [ $# -eq 0 ]; then
  echo "Running main.py..."
  uv run mpremote run src/main.py
else
  echo "Running $@..."
  uv run mpremote run $@
fi
