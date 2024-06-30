import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from google.api_core.exceptions import RetryError, ServiceUnavailable
from HelperTA import HelperTA
from DataChart import DataChart
import matplotlib.pyplot as plt


class DataCaching:
    def __init__(self, db, table='paper_data'):
        print("Initializing DataCaching...")
        self.db = db
        self.table = table
        self.tickers = []
        self.timeframes = {
            '1min': {'interval': '1m', 'period': 'max'},
            '1h': {'interval': '1h', 'period': '3mo'},
            '1D': {'interval': '1d', 'period': 'max'}
        }
        self.max_datapoints = 250
        self.helper_ta = HelperTA()

    def setTickers(self, tickers=[]):
        print(f"Setting tickers: {tickers}")
        self.tickers = tickers

    def init(self):
        print("Initializing data...")
        for timeframe, params in self.timeframes.items():
            print(f"Downloading data for {self.tickers} on {timeframe} timeframe...")
            try:
                data = yf.download(tickers=self.tickers, interval=params['interval'], period=params['period'], group_by='ticker')
                print(f"Downloaded data for {self.tickers} on {timeframe} timeframe.")
                for ticker in self.tickers:
                    if ticker in data:
                        ticker_data = data[ticker]
                        if len(ticker_data) >= 220:
                            try:
                                ticker_data = self._calculate_market_cycle(ticker_data)
                                print(f"== Ticker :: {ticker} ==")
                                print(ticker_data.tail(10))
                                if timeframe == '1D':
                                    self._generate_and_save_5d_data(ticker, ticker_data)
                                ticker_data = self._trim_data(ticker_data)
                                self._save_to_firestore(ticker, timeframe, ticker_data)
                            except (RetryError, ServiceUnavailable) as e:
                                print(f"Error saving data to Firestore for {ticker} on {timeframe} timeframe: {e}")
                                print("Please check your internet connection and Google Cloud credentials.")
                        else:
                            print(f"Not enough data for {ticker} on {timeframe} timeframe")
                    else:
                        print(f"No data found for {ticker} on {timeframe} timeframe")
            except Exception as e:
                print(f"Error downloading data for {self.tickers} on {timeframe} timeframe: {e}")
                continue

        # Generate the combined market cycle dataseries for each ticker
        for ticker in self.tickers:
            try:
                print(f"Generating combined market cycle data for {ticker}...")
                df_1min = self.get_data(ticker, '1min')
                df_1h = self.get_data(ticker, '1h')
                df_1d = self.get_data(ticker, '1D')
                df_5d = self.get_data(ticker, '5D')

                if df_1min is not None:
                    combined_df = df_1min.copy()
                    combined_df['marketCycle_1m'] = df_1min['marketCycle']

                    if df_1h is not None:
                        combined_df['marketCycle_1h'] = df_1h['marketCycle'].reindex(combined_df.index, method='nearest')
                    if df_1d is not None:
                        combined_df['marketCycle_1d'] = df_1d['marketCycle'].reindex(combined_df.index, method='nearest')
                    if df_5d is not None:
                        combined_df['marketCycle_5d'] = df_5d['marketCycle'].reindex(combined_df.index, method='nearest')
                    
                    self._save_to_firestore(ticker, 'mc', combined_df)

            except Exception as e:
                print(f"Error generating combined market cycle data for {ticker}: {e}")

    def _generate_and_save_5d_data(self, ticker, df_1d_untrimmed):
        try:
            print(f"Generating 5D data for {ticker} from 1D data...")
            df_5d = self._resample_to_5d(df_1d_untrimmed)
            df_5d = self._calculate_market_cycle(df_5d)
            self._save_to_firestore(ticker, '5D', df_5d)
        except Exception as e:
            print(f"Error generating 5D data for {ticker}: {e}")
            
    def update_data(self):
        print("Updating data...")
        for timeframe, params in self.timeframes.items():
            print(f"Updating data for {self.tickers} on {timeframe} timeframe...")
            try:
                data = yf.download(tickers=self.tickers, interval=params['interval'], period='1d', group_by='ticker')
                print(f"Downloaded latest data for {self.tickers} on {timeframe} timeframe.")
                for ticker in self.tickers:
                    if ticker in data:
                        new_data = data[ticker]
                        if not new_data.empty:
                            try:
                                existing_data = self.get_data(ticker, timeframe, trim=False)
                                if existing_data is not None:
                                    combined_data = pd.concat([existing_data, new_data]).drop_duplicates().sort_index()
                                    combined_data = self._calculate_market_cycle(combined_data)
                                    if timeframe == '1D':
                                        self._generate_and_save_5d_data(ticker, combined_data)
                                    combined_data = self._trim_data(combined_data)
                                    self._save_to_firestore(ticker, timeframe, combined_data)
                                else:
                                    print(f"No existing data found for {ticker} on {timeframe} timeframe, initializing.")
                                    new_data = self._calculate_market_cycle(new_data)
                                    self._save_to_firestore(ticker, timeframe, new_data)
                            except (RetryError, ServiceUnavailable) as e:
                                print(f"Error updating data to Firestore for {ticker} on {timeframe} timeframe: {e}")
                                print("Please check your internet connection and Google Cloud credentials.")
                        else:
                            print(f"No new data found for {ticker} on {timeframe} timeframe")
                    else:
                        print(f"No data found for {ticker} on {timeframe} timeframe")
            except Exception as e:
                print(f"Error updating data for {self.tickers} on {timeframe} timeframe: {e}")
                continue

        # Generate the combined market cycle dataseries for each ticker
        for ticker in self.tickers:
            try:
                print(f"Generating combined market cycle data for {ticker}...")
                df_1min = self.get_data(ticker, '1min')
                df_1h = self.get_data(ticker, '1h')
                df_1d = self.get_data(ticker, '1D')
                df_5d = self.get_data(ticker, '5D')

                if df_1min is not None:
                    combined_df = df_1min.copy()
                    combined_df['marketCycle_1m'] = df_1min['marketCycle']

                    if df_1h is not None:
                        combined_df['marketCycle_1h'] = df_1h['marketCycle'].reindex(combined_df.index, method='nearest')
                    if df_1d is not None:
                        combined_df['marketCycle_1d'] = df_1d['marketCycle'].reindex(combined_df.index, method='nearest')
                    if df_5d is not None:
                        combined_df['marketCycle_5d'] = df_5d['marketCycle'].reindex(combined_df.index, method='nearest')
                    
                    self._save_to_firestore(ticker, 'mc', combined_df)

            except Exception as e:
                print(f"Error generating combined market cycle data for {ticker}: {e}")



    def _calculate_market_cycle(self, _data):
        data = _data.copy()
        data = data.dropna(subset=[col for col in data.columns if col != 'marketCycle'])
        donchianPrice = data['Close']
        rsiPrice = data['Close']
        srsiPrice = data['Close']
        donchianPeriod = 14
        donchianSmoothing = 3
        rsiPeriod = 14
        rsiSmoothing = 3
        srsiPeriod = 20
        srsiSmoothing = 3
        srsiK = 5
        srsiD = 5
        rsiWeight = 0.5
        srsiWeight = 1.0
        dcoWeight = 1.0

        market_cycle = self.helper_ta.MarketCycle(donchianPrice, rsiPrice, srsiPrice, donchianPeriod, donchianSmoothing, rsiPeriod, rsiSmoothing, srsiPeriod, srsiSmoothing, srsiK, srsiD, rsiWeight, srsiWeight, dcoWeight)
        data = data.copy()
        data['marketCycle'] = market_cycle  # Use a copy of the data to avoid SettingWithCopyWarning
        return data

    def _save_to_firestore(self, ticker, timeframe, data, trim=True):
        print(f"Saving data for {ticker} on {timeframe} timeframe to Firestore...")
        doc_ref = self.db.collection(self.table).document(f"{ticker}_{timeframe}")
        
        data_reset = data.reset_index()
        datetime_col = 'Datetime' if 'Datetime' in data_reset.columns else 'Date'
        print(f"Datetime column name: {datetime_col}")
        
        data_list = data_reset.to_dict('records')
        
        if trim and len(data_list) > self.max_datapoints:
            print(f"Trimming data from {len(data_list)} to {self.max_datapoints} datapoints")
            data_list = data_list[-self.max_datapoints:]
        
        doc_data = {
            'ticker': ticker,
            'timeframe': timeframe,
            'latest_timestamp': data_list[-1][datetime_col].timestamp(),
            'data': [{k: (v.timestamp() if k == datetime_col else v) for k, v in item.items()} for item in data_list]
        }
        
        print(f"Saving document with {len(doc_data['data'])} datapoints...")
        doc_ref.set(doc_data)
        print(f"Saved data for {ticker} on {timeframe} timeframe")

    def _update_firestore(self, ticker, timeframe, new_data):
        doc_ref = self.db.collection(self.table).document(f"{ticker}_{timeframe}")
        
        # Get existing data
        doc = doc_ref.get()
        existing_data = doc.to_dict()['data']
        
        # Reset index to make sure datetime is a column
        new_data_reset = new_data.reset_index()
        
        # Determine the name of the datetime column
        datetime_col = 'Datetime' if 'Datetime' in new_data_reset.columns else 'Date'
        
        # Convert new_data to list of dictionaries and combine with existing data
        new_data_list = [{k: (v.timestamp() if k == datetime_col else v) for k, v in item.items()} 
                         for item in new_data_reset.to_dict('records')]
        combined_data = existing_data + new_data_list
        
        # Trim to max_datapoints if necessary
        if len(combined_data) > self.max_datapoints:
            combined_data = combined_data[-self.max_datapoints:]
        
        # Prepare update data
        update_data = {
            'latest_timestamp': combined_data[-1][datetime_col],
            'data': combined_data
        }
        
        doc_ref.update(update_data)
        print(f"Updated data for {ticker} on {timeframe} timeframe")

    def _resample_to_5d(self, data):
        # Resample to 5-day intervals (Monday to Friday)
        data_5d = data.resample('5D').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Adj Close': 'last',
            'Volume': 'sum'
        }).dropna()
        return data_5d

    def _trim_data(self, data):
        if len(data) > self.max_datapoints:
            print(f"Trimming data from {len(data)} to {self.max_datapoints} datapoints")
            data = data.iloc[-self.max_datapoints:]
        return data

    def get_data(self, ticker, timeframe, trim=True):
        doc_ref = self.db.collection(self.table).document(f"{ticker}_{timeframe}")
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()['data']
            df = pd.DataFrame(data)
            datetime_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
            df[datetime_col] = pd.to_datetime(df[datetime_col], unit='s')
            if trim and len(df) > self.max_datapoints:
                df = df.iloc[-self.max_datapoints:]
            return df.set_index(datetime_col)
        else:
            return None
        
    def chart(self, ticker, output_filename='image.png'):
        data = self.get_data(ticker, 'mc')
        if data is not None:
            chart = DataChart(data)
            chart.plot_subplots([
                ['Close'],  # Assuming 'Close' price is used for the main chart
                ['marketCycle_1m', 'marketCycle_1h', 'marketCycle_1d', 'marketCycle_5d', 20, 50, 80]
            ], output_filename=output_filename)
        else:
            print(f"No data available for {ticker} to generate chart.")
