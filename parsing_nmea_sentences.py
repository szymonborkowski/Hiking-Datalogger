"""
Initial script to get started with NMEA sentence parsing

Beginning with Python for ease of use but this might transition onto the Arduino if the computation capability/memory will allow it
"""

import os

def filter_nmea_sentences(input_filename, output_filename, sentence_prefix):
    try:
        # 1. Read and Filter
        with open(input_filename, 'r') as infile:
            # Use a list comprehension to read all lines and filter them
            # .strip() removes any leading/trailing whitespace, including newline
            # .startswith() checks the required prefix
            filtered_lines = [
                line.strip()
                for line in infile
                if line.strip().startswith(sentence_prefix)
            ]

        # 2. Write to Output File
        if filtered_lines:
            # We add the newline character back when writing to the file
            output_content = '\n'.join(filtered_lines) + '\n'
            
            with open(output_filename, 'w') as outfile:
                outfile.write(output_content)
                
            print(f"Filtered {len(filtered_lines)} lines.")
            print(f"Output saved to: {output_filename}")
        else:
            print(f"No lines starting with '{sentence_prefix}' were found in the input file.")
            
    except FileNotFoundError:
        print(f"Error: The input file '{input_filename}' was not found.")
    except IOError as e:
        print(f"An error occurred during file operation: {e}")

INPUT_FILE = "initial_gps_data.txt"
OUTPUT_FILE = "output.txt"
TARGET_PREFIX = "$GPGSV"  # The prefix to filter for

if __name__ == "__main__":
        
    filter_nmea_sentences(INPUT_FILE, OUTPUT_FILE, TARGET_PREFIX)
