"""
Script for NMEA sentence parsing.

Contains a number of methods that extract information of interest from the txt file created by the Arduino.
"""

import matplotlib.pyplot as plt
import os

def filter_nmea_sentences_by_prefix(input_filename, output_filename, sentence_prefix):
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


def extract_gpvtg_speed(input_file, output_file):
    """
    Reads a text file, finds full $GPVTG lines, and extracts the 
    speed in km/h (7th index after splitting by comma) to an output file.
    """
    
    # Check if input file exists to avoid errors
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' was not found.")
        return

    count = 0
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                line = line.strip()
                
                # 1. Filter: Ensure line is not empty and starts with the correct ID
                if not line or not line.startswith('$GPVTG'):
                    continue
                
                parts = line.split(',')
                
                # 2. Filter: Ensure line is 'complete' enough to have our target value.
                # In '$GPVTG,102.01,T,,M,21.46,N,39.76,K,A*35', the value 39.76 is at index 7.
                # Therefore, we need at least 8 parts (index 0 to 7).
                if len(parts) > 7:
                    target_value = parts[7]
                    
                    # Optional: Check if the value is actually a number (not empty)
                    if target_value:
                        outfile.write(target_value + '\n')
                        count += 1
                        
        print(f"Success! Processed {count} valid lines.")
        print(f"Data saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


def top_speed(input_file):
    top_num = 0

    with open(input_file, 'r') as file:
        for line in file:
            current_num = float(line)
            if (current_num > top_num):
                top_num = current_num

    print("Top speed is: " + str(top_num))


def plot_gpvtg_speed(input_file):
    """
    Reads a GPS text file, extracts speed values from valid $GPVTG lines,
    and plots them using matplotlib.
    """
    speeds = []
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    try:
        i = 0
        with open(input_file, 'r') as infile:
            for line in infile:

                line = line.strip()

                
                # Filter for valid ID
                if not line or not line.startswith('$GPVTG'):
                    continue
                
                parts = line.split(',')
                
                # Filter for complete lines (must have index 7)
                if len(parts) > 7:
                    raw_value = parts[7]
                    
                    # Convert to float for plotting
                    try:
                        if raw_value:
                            val = float(raw_value)
                            speeds.append(val)
                    except ValueError:
                        continue


        # Check if we found data
        if not speeds:
            print("No valid speed data found to plot.")
            return

        # Generate the Plot
        plt.figure(figsize=(10, 6))
        plt.plot(speeds, marker='o', linestyle='-', color='blue', linewidth=1, markersize=3)
        
        plt.title("Speed Over Time")
        plt.xlabel("Sample Index (Arbitrary Time)")
        plt.ylabel("Speed (km/h)")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save and show
        output_filename = 'speed_plot.png'
        plt.savefig(output_filename)
        print(f"Plot saved successfully to '{output_filename}'")
        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
        
    filter_nmea_sentences_by_prefix("car_journey.txt", "output_1.txt", "$GPVTG")

    extract_gpvtg_speed("output_1.txt", "output_2.txt")

    top_speed("output_2.txt")

    plot_gpvtg_speed("output_1.txt")

