# prompt: list all the data_*.csv files, load with pandas, and display the name and row number of the files that have NaN or missing values

import pandas as pd
import glob

# Get a list of files matching the pattern 'data_*.csv'
files = glob.glob('../../data/*.csv')

# Initialize counters
total_lines = 0
total_true_labels = 0

# Loop through each file
for file in files:
    # Read the file into a pandas DataFrame
    df = pd.read_csv(file)

    # Check for missing values
    missing_values = df.isnull().sum().sum()

    # Print statistics for the current file
    print(f"File: {file}")
    print(f"Number of lines: {len(df)}")
    print(f"Number of missing values: {missing_values}")

    # If there are missing values, display the file name and row number
    if missing_values > 0:
        print("Rows with missing values:")
        for i, row in df.iterrows():
            if row.isnull().any():
                print(f"Row {i + 1}: {row}")

    print()
