import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 500)
from DataCaching import DataCaching
import glob

import requests
from bs4 import BeautifulSoup

download = False
export = False
stats = False
fix = True

symbols = [
    "PLTR",
    "GME",
    "AMC",
    "NVDA",
    "ETH-USD",
    "BTC-USD",
    "DOGE-USD",
    "ARM",
    "AMSC",
    "GOOG"
]

def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip()
        tickers.append(ticker)
    return tickers

symbols = get_sp500_tickers()

if download == True:
    print("== DOWNLOADING ==")
    cache = DataCaching(output="file", max_datapoints=100000)
    cache.setTickers(symbols)
    cache.init()
    print("Done!")


def calculate_deltas_and_values(df, column_prefix):
    df[f'{column_prefix}_value1'] = df[column_prefix].shift(1)
    df[f'{column_prefix}_value2'] = df[column_prefix].shift(2)
    df[f'{column_prefix}_value3'] = df[column_prefix].shift(3)

    df[f'{column_prefix}_delta0'] = df[column_prefix] - df[f'{column_prefix}_value1']
    df[f'{column_prefix}_delta1'] = df[f'{column_prefix}_value1'] - df[f'{column_prefix}_value2']
    df[f'{column_prefix}_delta2'] = df[f'{column_prefix}_value2'] - df[f'{column_prefix}_value3']

    return df

def ensure_timezone_consistency(df, reference_df):
    if reference_df.index.tz is not None:
        if df.index.tz is None:
            df.index = df.index.tz_localize(reference_df.index.tz)
        else:
            df.index = df.index.tz_convert(reference_df.index.tz)
    else:
        df.index = df.index.tz_localize(None)
    return df

def buildTrainingData(ticker="AMC", n=120, threshold=1.0):
    # Load all timeframes
    df_1min = pd.read_csv(f"./data/{ticker}_1min.csv", index_col=0, parse_dates=True)
    df_1h = pd.read_csv(f"./data/{ticker}_1h.csv", index_col=0, parse_dates=True)
    df_1d = pd.read_csv(f"./data/{ticker}_1D.csv", index_col=0, parse_dates=True)
    df_5d = pd.read_csv(f"./data/{ticker}_5D.csv", index_col=0, parse_dates=True)

    # Ensure timezone consistency
    df_1h = ensure_timezone_consistency(df_1h, df_1min)
    df_1d = ensure_timezone_consistency(df_1d, df_1min)
    df_5d = ensure_timezone_consistency(df_5d, df_1min)

    # Calculate deltas and values for each timeframe
    df_1min = calculate_deltas_and_values(df_1min, 'marketCycle')
    df_1h = calculate_deltas_and_values(df_1h, 'marketCycle')
    df_1d = calculate_deltas_and_values(df_1d, 'marketCycle')
    df_5d = calculate_deltas_and_values(df_5d, 'marketCycle')

    # Resample 1min data to match other timeframes
    df_1min_resampled = df_1min.resample('min').asfreq()
    df_1h_resampled = df_1h.resample('min').ffill()
    df_1d_resampled = df_1d.resample('min').ffill()
    df_5d_resampled = df_5d.resample('min').ffill()

    # Combine dataframes
    df_combined = df_1min_resampled.copy()
    df_combined = df_combined.join(df_1h_resampled, rsuffix='_1h')
    df_combined = df_combined.join(df_1d_resampled, rsuffix='_1d')
    df_combined = df_combined.join(df_5d_resampled, rsuffix='_5d')

    # Reset index to make 'Datetime' a column
    df_combined.reset_index(inplace=True)
    df_combined.rename(columns={'index': 'Datetime'}, inplace=True)

    # Calculate additional fields
    df_combined["high_10"] = df_combined["High"].shift(-n).rolling(n).max()
    df_combined["diff_10"] = df_combined["high_10"] - df_combined["Open"]
    df_combined["max_10"] = (df_combined["high_10"] - df_combined["Open"]) / df_combined["Open"] * 100
    df_combined["label"] = df_combined["max_10"] > threshold

    # Drop NaN values
    df_combined = df_combined.dropna()

    # Select relevant columns
    columns = ["marketCycle", "marketCycle_value1", "marketCycle_value2", "marketCycle_value3", 
               "marketCycle_delta0", "marketCycle_delta1", "marketCycle_delta2", "marketCycle_1h", "marketCycle_value1_1h",
               "marketCycle_value2_1h", "marketCycle_value3_1h", "marketCycle_delta0_1h", "marketCycle_delta1_1h",
               "marketCycle_delta2_1h", "marketCycle_1d", "marketCycle_value1_1d", "marketCycle_value2_1d", 
               "marketCycle_value3_1d", "marketCycle_delta0_1d", "marketCycle_delta1_1d", "marketCycle_delta2_1d", 
               "marketCycle_5d", "marketCycle_value1_5d", "marketCycle_value2_5d", "marketCycle_value3_5d", 
               "marketCycle_delta0_5d", "marketCycle_delta1_5d", "marketCycle_delta2_5d", "label"]
    
    df_combined = df_combined[columns]
    total_over_threshold = len(df_combined[df_combined['label'] == True])

    if len(df_combined) > 100:
        # Calculate percentage of rows where max_10 >= 1.0
        percentage = total_over_threshold / len(df_combined) * 100
        print(f"max_10 >= 1.0: {percentage:.2f}% ({total_over_threshold}/{len(df_combined)})")
        if total_over_threshold > 0:
            df_combined.to_csv(f"./data/data_{ticker}.csv")
    else:
        print("No data left")

    return df_combined



if export == True:
    print("== EXPORTING ==")
    for symbol in symbols:
        print(f"\n\n== {symbol} ==")
        try:
            df_training = buildTrainingData(symbol, n=60, threshold=1.5)
        except:
            print("Error :(")
    print("Done!")

if stats == True:
    print("== STATS ==")
    # Get a list of files matching the pattern 'data_*.csv'
    files = glob.glob('./data/data_*.csv')

    # Initialize counters
    total_lines = 0
    total_true_labels = 0

    # Loop through each file
    for file in files:
        # Read the file into a pandas DataFrame
        df = pd.read_csv(file)

        # Get the number of rows in the current file
        num_lines = len(df)

        # Get the number of rows where 'label' is True
        num_true_labels = len(df[df['label'] == True])

        # Update the total counters
        total_lines += num_lines
        total_true_labels += num_true_labels

        # Print statistics for the current file
        print(f"{file}: {num_true_labels} / {num_lines}")

    # Print the total statistics
    print(f"Total: {total_true_labels}/{total_lines}")

if fix == True:
    # Get a list of files matching the pattern 'data_*.csv'
    files = glob.glob('./data/data_*.csv')

    # Loop through each file
    for file in files:
        # Read the file into a pandas DataFrame
        df = pd.read_csv(file)

        # Remove the first column
        df.drop(columns=df.columns[0], inplace=True)

        # Save the DataFrame to a new file without index
        new_file_name = file
        df.to_csv(new_file_name, index=False)
