import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class StockDataProcessor:
    def __init__(self, model="up", name="up", useShortData=False, use_sp500=True, download=False, export=True, stats=True, fix=True, batch_size=10, export_threshold=1.5, export_n=60):
        self.model = model
        self.name = name
        self.use_sp500 = use_sp500
        self.download = download
        self.export = export
        self.stats = stats
        self.fix = fix
        self.batch_size = batch_size
        self.useShortData = useShortData
        self.symbols = [
            "PLTR", "GME", "AMC", "NVDA", "ETH-USD", "BTC-USD", "DOGE-USD", "ARM", "AMSC", "GOOG"
        ]
        if use_sp500:
            self.symbols = self.get_sp500_tickers()
        self.export_threshold = export_threshold
        self.export_n = export_n
        #self._set_export_params()

    def _set_export_params(self):
        if self.model == "buy":
            self.export_threshold = 1.5
            self.export_n = 60
        elif self.model == "sell":
            self.export_threshold = -1.5
            self.export_n = 60
        elif self.model == "up":
            self.export_threshold = None
            self.export_n = 3
        elif self.model == "down":
            self.export_threshold = None
            self.export_n = 3

    def get_sp500_tickers(self):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text.strip()
            tickers.append(ticker)
        return tickers

    def download_data(self):
        print("== DOWNLOADING ==")
        cache = DataCaching(output="file", max_datapoints=100000)
        cache.setTickers(self.symbols)
        cache.init()
        print("Done!")

    def calculate_deltas_and_values(self, df, column_prefix):
        df[f'{column_prefix}_value1'] = df[column_prefix].shift(1)
        df[f'{column_prefix}_value2'] = df[column_prefix].shift(2)
        df[f'{column_prefix}_value3'] = df[column_prefix].shift(3)

        df[f'{column_prefix}_delta0'] = df[column_prefix] - df[f'{column_prefix}_value1']
        df[f'{column_prefix}_delta1'] = df[f'{column_prefix}_value1'] - df[f'{column_prefix}_value2']
        df[f'{column_prefix}_delta2'] = df[f'{column_prefix}_value2'] - df[f'{column_prefix}_value3']

        return df

    def ensure_timezone_consistency(self, df, reference_df):
        if reference_df.index.tz is not None:
            if df.index.tz is None:
                df.index = df.index.tz_localize(reference_df.index.tz)
            else:
                df.index = df.index.tz_convert(reference_df.index.tz)
        else:
            df.index = df.index.tz_localize(None)
        return df

    def build_training_data(self, ticker, n, threshold):
        try:
            # Load all timeframes
            df_1min = pd.read_csv(f"./data/{ticker}_1min.csv", index_col=0, parse_dates=True)
            df_1h = pd.read_csv(f"./data/{ticker}_1h.csv", index_col=0, parse_dates=True)
            df_1d = pd.read_csv(f"./data/{ticker}_1D.csv", index_col=0, parse_dates=True)
            df_5d = pd.read_csv(f"./data/{ticker}_5D.csv", index_col=0, parse_dates=True)

            # Ensure timezone consistency
            df_1h = self.ensure_timezone_consistency(df_1h, df_1min)
            df_1d = self.ensure_timezone_consistency(df_1d, df_1min)
            df_5d = self.ensure_timezone_consistency(df_5d, df_1min)

            # Calculate deltas and values for each timeframe
            df_1min = self.calculate_deltas_and_values(df_1min, 'marketCycle')
            df_1h = self.calculate_deltas_and_values(df_1h, 'marketCycle')
            df_1d = self.calculate_deltas_and_values(df_1d, 'marketCycle')
            df_5d = self.calculate_deltas_and_values(df_5d, 'marketCycle')

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
            if self.model == "buy":
                df_combined["high_10"] = df_combined["High"].shift(-n).rolling(n).max()
                df_combined["diff_10"] = df_combined["high_10"] - df_combined["Open"]
                df_combined["max_10"] = (df_combined["high_10"] - df_combined["Open"]) / df_combined["Open"] * 100
                df_combined["label"] = df_combined["max_10"] >= threshold
            elif self.model == "sell":
                df_combined["low_10"] = df_combined["Low"].shift(-n).rolling(n).min()
                df_combined["diff_10"] = df_combined["low_10"] - df_combined["Open"]
                df_combined["min_10"] = (df_combined["low_10"] - df_combined["Open"]) / df_combined["Open"] * 100
                df_combined["label"] = df_combined["min_10"] <= threshold
            elif self.model == "up":
                df_combined["label"] = df_combined["Close"].shift(-n).rolling(n).mean() > df_combined["Close"]
            elif self.model == "down":
                df_combined["label"] = df_combined["Close"].shift(-n).rolling(n).mean() < df_combined["Close"]

            # Drop NaN values
            df_combined = df_combined.dropna()

            # Select relevant columns
            if self.useShortData == True:
                columns = ["marketCycle", "marketCycle_value1", "marketCycle_value2", "marketCycle_value3", 
                       "marketCycle_1h", "marketCycle_value1_1h", "marketCycle_value2_1h", "marketCycle_value3_1h", 
                       "marketCycle_1d", "marketCycle_value1_1d", "marketCycle_value2_1d", "marketCycle_value3_1d",
                       "marketCycle_5d", "marketCycle_value1_5d", "marketCycle_value2_5d", "marketCycle_value3_5d", 
                       "label"]
            else:
                columns = ["marketCycle", "marketCycle_value1", "marketCycle_value2", "marketCycle_value3", 
                       "marketCycle_delta0", "marketCycle_delta1", "marketCycle_delta2", "marketCycle_1h", "marketCycle_value1_1h",
                       "marketCycle_value2_1h", "marketCycle_value3_1h", "marketCycle_delta0_1h", "marketCycle_delta1_1h",
                       "marketCycle_delta2_1h", "marketCycle_1d", "marketCycle_value1_1d", "marketCycle_value2_1d", 
                       "marketCycle_value3_1d", "marketCycle_delta0_1d", "marketCycle_delta1_1d", "marketCycle_delta2_1d", 
                       "marketCycle_5d", "marketCycle_value1_5d", "marketCycle_value2_5d", "marketCycle_value3_5d", 
                       "marketCycle_delta0_5d", "marketCycle_delta1_5d", "marketCycle_delta2_5d", "label"]

            df_combined = df_combined[columns]
            
            if self.model == "up" or self.model == "down":
                df_combined[df_combined.columns.difference(['label'])] = df_combined[df_combined.columns.difference(['label'])].round().astype(int)
            
            total_over_threshold = len(df_combined[df_combined['label'] == True])
            if len(df_combined) > 100:
                # Calculate percentage of rows where max_10 >= 1.0
                percentage = total_over_threshold / len(df_combined) * 100
                print(f"max_10 >= 1.0: {percentage:.2f}% ({total_over_threshold}/{len(df_combined)})")
                if total_over_threshold > 0:
                    df_combined.to_csv(f"../data/{self.name}_{ticker}.csv")
            else:
                print(f"No data left for {ticker}")

            return df_combined
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    def export_datasets(self):
        print("== EXPORTING ==")
        batch_size = self.batch_size
        for i in range(0, len(self.symbols), batch_size):
            batch_symbols = self.symbols[i:i + batch_size]
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(self.build_training_data, symbol, self.export_n, self.export_threshold): symbol for symbol in batch_symbols}
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result = future.result()
                        if result is not None:
                            print(f"Processed {symbol} successfully.")
                        else:
                            print(f"No data for {symbol}.")
                    except Exception as e:
                        print(f"Error processing {symbol}: {e}")
        print("Done!")

    def display_stats(self):
        print("== STATS ==")
        files = glob.glob(f'../data/{self.name}_*.csv')
        total_lines, total_true_labels = 0, 0

        for file in files:
            df = pd.read_csv(file)
            num_lines = len(df)
            num_true_labels = len(df[df['label'] == True])

            total_lines += num_lines
            total_true_labels += num_true_labels

            print(f"{file}: {num_true_labels} / {num_lines}")

        print(f"Total: {total_true_labels}/{total_lines}")

    def fix_datasets(self):
        print("== FIXING DATASETS ==")
        files = glob.glob(f'../data/{self.name}_*.csv')
        for file in files:
            df = pd.read_csv(file)
            df.drop(columns=df.columns[0], inplace=True)
            df.to_csv(file, index=False)

    def run(self):
        if self.use_sp500:
            self.symbols = self.get_sp500_tickers()

        if self.download:
            self.download_data()

        if self.export:
            self.export_datasets()

        if self.stats:
            self.display_stats()

        if self.fix:
            self.fix_datasets()

if __name__ == "__main__":
    processor = StockDataProcessor(model="down", name="grid-down-5", useShortData=True, export_threshold=1.0, export_n=5, use_sp500=True, download=False, export=True, stats=True, fix=True, batch_size=2)
    processor.run()
