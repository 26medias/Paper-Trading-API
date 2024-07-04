from DataCaching import DataCaching

export = True

cache = DataCaching(output="file", max_datapoints=100000)
cache.setTickers([
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
])
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

def buildTrainingData(ticker="AMC", n=120):
    # Load all timeframes
    df_1min = pd.read_csv(f"./{ticker}_1min.csv", index_col=0, parse_dates=True)
    df_1h = pd.read_csv(f"./{ticker}_1h.csv", index_col=0, parse_dates=True)
    df_1d = pd.read_csv(f"./{ticker}_1D.csv", index_col=0, parse_dates=True)
    df_5d = pd.read_csv(f"./{ticker}_5D.csv", index_col=0, parse_dates=True)

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
    df_1min_resampled = df_1min.resample('1T').asfreq()
    df_1h_resampled = df_1h.resample('1T').ffill()
    df_1d_resampled = df_1d.resample('1T').ffill()
    df_5d_resampled = df_5d.resample('1T').ffill()

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

    # Drop NaN values
    df_combined = df_combined.dropna()

    # Select relevant columns
    columns = ["marketCycle", "marketCycle_value1", "marketCycle_value2", "marketCycle_value3", 
               "marketCycle_delta0", "marketCycle_delta1", "marketCycle_delta2", "marketCycle_1h", "marketCycle_value1_1h",
               "marketCycle_value2_1h", "marketCycle_value3_1h", "marketCycle_delta0_1h", "marketCycle_delta1_1h",
               "marketCycle_delta2_1h", "marketCycle_1d", "marketCycle_value1_1d", "marketCycle_value2_1d", 
               "marketCycle_value3_1d", "marketCycle_delta0_1d", "marketCycle_delta1_1d", "marketCycle_delta2_1d", 
               "marketCycle_5d", "marketCycle_value1_5d", "marketCycle_value2_5d", "marketCycle_value3_5d", 
               "marketCycle_delta0_5d", "marketCycle_delta1_5d", "marketCycle_delta2_5d", "max_10"]
    
    df_combined = df_combined[columns]

    # Calculate percentage of rows where max_10 >= 1.0
    percentage = len(df_combined[df_combined['max_10'] >= 1.0]) / len(df_combined) * 100
    print(f"max_10 >= 1.0: {percentage:.2f}% (total: {len(df_combined)})")

    return df_combined



if export == True:
    df_training = buildTrainingData("AMSC", n=20)
    print(df_training.tail(100))