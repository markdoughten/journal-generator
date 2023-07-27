#!/bin/bash

# Directory to scan
dir="Archive"

# Path to the converter
converter="./convert-ichat-files/Build/Convert ichat Files"

# Loop through .ichat files in the directory and its sub-directories
find "$dir" -type f -name "*.ichat" | while read file; do
    # Define the new file name by replacing .ichat with .txt
    new_file=$(echo "$file" | sed 's/\.ichat$/\.txt/')
  
    # Execute the conversion command
    "$converter" -mode convert -format 'TXT' -input "$file"
    
    # Add the original filename as the first line of each converted txt file
    echo "$file" | cat - "$new_file" > temp && mv temp "$new_file"
done

