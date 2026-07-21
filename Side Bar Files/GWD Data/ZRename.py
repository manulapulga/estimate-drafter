import os

# Use the current working directory (i.e., where the script is saved)
folder_path = os.getcwd()

# Prefix to remove
prefix = "GWD Revised Rates Based on DSR 21_"

# Iterate through files and rename
for filename in os.listdir(folder_path):
    if filename.startswith(prefix):
        new_name = filename[len(prefix):]
        os.rename(filename, new_name)
        print(f'Renamed: {filename} → {new_name}')