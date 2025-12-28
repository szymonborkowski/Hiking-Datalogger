"""
Script for NMEA sentence parsing.

Contains a number of methods that extract information of interest from the txt file created by the Arduino.
"""

import matplotlib.pyplot as plt
import os
import math

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

def nmea_to_decimal(value, direction):
    """
    Converts NMEA format (DDMM.MMMM) to decimal degrees (DD.DDDD).
    Example: 4807.038 becomes 48 + (07.038 / 60) = 48.1173
    """
    try:
        # NMEA format is [Degrees][Minutes].[Decimals]
        # Assume the last two whole digits before the decimal are minutes.
        
        # Ensure the value is a float
        val_float = float(value)
        
        # Separate degrees from minutes
        degrees = int(val_float / 100)
        minutes = val_float - (degrees * 100)
        
        decimal_degrees = degrees + (minutes / 60)
        
        # Handle Hemisphere
        if direction.upper() in ['S', 'W']:
            decimal_degrees *= -1
            
        return decimal_degrees
    except ValueError:
        return None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates distance between two points on Earth in Meters.
    """
    R = 6371000  # radius of Earth in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def process_gps_data(input_file):
    total_distance = 0.0
    previous_point = None  # Tuple (lat, lon)

    with open(input_file, 'r') as infile:
        for sentence in infile:
            parts = sentence.split(',')
            
            # 1. Basic format check
            if not sentence.startswith('$GPRMC'):
                continue
                
            # 2. Check for incomplete sentences (Standard GPRMC has ~12 fields)
            if len(parts) < 10:
                continue

            # 3. Check 'Status' flag (Index 2). 'A' = Active (Valid), 'V' = Void (Invalid)
            status = parts[2]
            if status != 'A':
                continue
                
            # 4. Extract and convert coordinates
            # Index 3: Lat, Index 4: N/S, Index 5: Lon, Index 6: E/W
            try:
                raw_lat = parts[3]
                lat_dir = parts[4]
                raw_lon = parts[5]
                lon_dir = parts[6]
                
                # Skip if fields are empty strings
                if not raw_lat or not raw_lon:
                    continue

                current_lat = nmea_to_decimal(raw_lat, lat_dir)
                current_lon = nmea_to_decimal(raw_lon, lon_dir)
                
                # 5. Calculate Distance
                added_dist = 0.0
                if previous_point is not None:
                    added_dist = haversine_distance(previous_point[0], previous_point[1], 
                                                    current_lat, current_lon)
                    
                    # Noise Threshold
                    # Ignore tiny movements (e.g., < 1 meter) to reduce GPS drift errors (modify as required)
                    if added_dist > 1.0: 
                        total_distance += added_dist
                    else:
                        added_dist = 0.0 # Treat as noise
                
                # Update previous point
                previous_point = (current_lat, current_lon)

            except Exception as e:
                print(f"ERROR - Parse Failed: {e}")
                continue

        return total_distance


if __name__ == "__main__":
        
    # Change prefix based on requirements
    filter_nmea_sentences_by_prefix("athlone_journey.txt", "output_coords.txt", "$GPRMC")

    # Speed data parsing:
    extract_gpvtg_speed("output_1.txt", "output_2.txt")
    top_speed("output_2.txt")
    plot_gpvtg_speed("output_1.txt")

    # Total distance parsing:
    total = process_gps_data("output_coords.txt")
