import pandas as pd
import numpy as np

# List of file paths to process.
# The instruction was to merge files starting with 'TCE_Callflow_Details_File_',
# but the provided file paths do not match this prefix.
# As per the context's 'Thought' section, all provided files will be merged.
file_paths = [
    'C:\\Users\\Anush\\AppData\\Local\\Temp\\tmpoe6fpy8h.xlsx',
    'C:\\Users\\Anush\\AppData\\Local\\Temp\\tmpi7jtc0ue.xlsx',
    'C:\\Users\\Anush\\AppData\\Local\\Temp\\tmpyvyuxg26.xlsx'
]

# Initialize an empty list to store dataframes
dfs = []

# Loop through each file path, read the Excel file, and append to the list
for file in file_paths:
    try:
        df = pd.read_excel(file)
        dfs.append(df)
    except FileNotFoundError:
        print(f"Error: File not found at {file}. Skipping this file.")
    except Exception as e:
        print(f"Error reading {file}: {e}. Skipping this file.")

# Check if any dataframes were successfully loaded
if not dfs:
    raise ValueError("No Excel files were successfully loaded. Cannot proceed with merging and processing.")

# Merge all dataframes into a single dataframe
merged_df = pd.concat(dfs, ignore_index=True)

# Define the volume columns that need numeric conversion and -8888 replacement
volume_columns = [
    'DL_Volume_5QI1_towards_UE',
    'UL_Volume_5QI1_from_UE',
    'DL_Volume_5QI2_towards_UE',
    'UL_Volume_5QI2_from_UE'
]

# Process volume columns: replace -8888 with NaN and convert to numeric
for col in volume_columns:
    if col in merged_df.columns:
        # Replace -8888 with NaN (will appear as blank)
        merged_df[col] = merged_df[col].replace(-8888, np.nan)
        # Convert to numeric, coercing errors to NaN
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    else:
        print(f"Warning: Column '{col}' not found in the merged dataframe. Skipping numeric conversion and -8888 replacement for this column.")

# Define description columns for NA replacement with blanks
# Columns 'RF_PUCCH_SINR_Desc' and 'RF_PUSCH_SINR_Desc' are not included as
# they were not found in the JSON inspection results, as per the context's 'Thought'.
desc_columns = [
    'RF_RSRP_Desc',
    'RF_RSRQ_Desc',
    'RF_Avg_CQI',
    'Mobility_RSRP_1_Desc'
]

# Replace NA values (NaN) with blanks (empty strings) in the specified description columns
for col in desc_columns:
    if col in merged_df.columns:
        # Replace any NA values (NaN, None) with an empty string ''
        # This handles various data types including numeric (will become object) and object (string)
        merged_df[col] = merged_df[col].fillna('')
    else:
        print(f"Warning: Column '{col}' not found in the merged dataframe. Skipping NA replacement for this column.")

# Display the first few rows of the processed dataframe and its info for verification
print("Processed Dataframe Head:")
print(merged_df.head())
print("\nProcessed Dataframe Info:")
merged_df.info()

# Example: Save the processed data to a new Excel file
# The output path can be adjusted as needed
output_file_path = 'processed_merged_data.xlsx'
try:
    merged_df.to_excel(output_file_path, index=False)
    print(f"\nProcessed data saved to {output_file_path}")
except Exception as e:
    print(f"Error saving processed data to {output_file_path}: {e}")