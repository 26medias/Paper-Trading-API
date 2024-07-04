import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from google.api_core.exceptions import RetryError, ServiceUnavailable
from HelperTA import HelperTA
from DataChart import DataChart
import matplotlib.pyplot as plt
import numpy as np
import json5
import os

class DataCaching:
    def __init__(self, db=None, table='paper_data', output='firestore', max_datapoints=250):
        print("Initializing DataCaching...")
        self.db = db
        self.table = table
        self.tickers = []
        self.timeframes = {
            '1min': {'interval': '1m', 'period': 'max'},
            '1h': {'interval': '1h', 'period': '3mo'},
            '1D': {'interval': '1d', 'period': 'max'}
        }
        self.max_datapoints = max_datapoints
        self.helper_ta = HelperTA()
        self.output = output  # firestore or file

    def setTickers(self, tickers=[]):
        print(f"Setting tickers: {tickers}")
        self.tickers = tickers

    def init(self):
        print("Initializing data...")
        for timeframe, params in self.timeframes.items():
            self._initialize_timeframe_data(timeframe, params)
        self._generate_combined_market_cycle_data()

    def update_data(self):
        print("Updating data...")
        for timeframe, params in self.timeframes.items():
            self._update_timeframe_data(timeframe, params)
        self._generate_combined_market_cycle_data()

    def _initialize_timeframe_data(self, timeframe, params):
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
                            if timeframe == '1D':
                                self._generate_and_save_5d_data(ticker, ticker_data)
                            ticker_data = self._trim_data(ticker_data)
                            self.save_data(ticker, timeframe, ticker_data)
                        except (RetryError, ServiceUnavailable) as e:
                            print(f"Error saving data for {ticker} on {timeframe} timeframe: {e}")
                            print("Please check your internet connection and Google Cloud credentials.")
                    else:
                        print(f"Not enough data for {ticker} on {timeframe} timeframe")
                else:
                    print(f"No data found for {ticker} on {timeframe} timeframe")
        except Exception as e:
            print(f"Error downloading data for {self.tickers} on {timeframe} timeframe: {e}")

    def _update_timeframe_data(self, timeframe, params):
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
                                if new_data.index.tz is not None:
                                    existing_data.index = existing_data.index.tz_convert(new_data.index.tz)
                                else:
                                    new_data.index = new_data.index.tz_localize(None)
                                combined_data = pd.concat([existing_data, new_data]).drop_duplicates().sort_index()
                                combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                                combined_data = self._calculate_market_cycle(combined_data)
                                if timeframe == '1D':
                                    self._generate_and_save_5d_data(ticker, combined_data)
                                combined_data = self._trim_data(combined_data)
                                self.save_data(ticker, timeframe, combined_data)
                            else:
                                print(f"No existing data found for {ticker} on {timeframe} timeframe, initializing.")
                                new_data = self._calculate_market_cycle(new_data)
                                self.save_data(ticker, timeframe, new_data)
                        except (RetryError, ServiceUnavailable) as e:
                            print(f"Error updating data for {ticker} on {timeframe} timeframe: {e}")
                            print("Please check your internet connection and Google Cloud credentials.")
                    else:
                        print(f"No new data found for {ticker} on {timeframe} timeframe")
                else:
                    print(f"No data found for {ticker} on {timeframe} timeframe")
        except Exception as e:
            print(f"Error updating data for {self.tickers} on {timeframe} timeframe: {e}")

    def _generate_combined_market_cycle_data(self):
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
                        df_1h = df_1h[~df_1h.index.duplicated(keep='last')]
                        if df_1h.index.tz is not None:
                            combined_df.index = combined_df.index.tz_convert(df_1h.index.tz)
                        else:
                            combined_df.index = combined_df.index.tz_localize(None)
                        combined_df['marketCycle_1h'] = df_1h['marketCycle'].reindex(combined_df.index, method='nearest')

                    if df_1d is not None:
                        df_1d = df_1d[~df_1d.index.duplicated(keep='last')]
                        if df_1d.index.tz is not None:
                            combined_df.index = combined_df.index.tz_convert(df_1d.index.tz)
                        else:
                            combined_df.index = combined_df.index.tz_localize(None)
                        combined_df['marketCycle_1d'] = df_1d['marketCycle'].reindex(combined_df.index, method='nearest')

                    if df_5d is not None:
                        df_5d = df_5d[~df_5d.index.duplicated(keep='last')]
                        if df_5d.index.tz is not None:
                            combined_df.index = combined_df.index.tz_convert(df_5d.index.tz)
                        else:
                            combined_df.index = combined_df.index.tz_localize(None)
                        combined_df['marketCycle_5d'] = df_5d['marketCycle'].reindex(combined_df.index, method='nearest')

                    self.save_data(ticker, 'mc', combined_df)

            except Exception as e:
                print(f"Error generating combined market cycle data for {ticker}: {e}")

    def _generate_and_save_5d_data(self, ticker, df_1d_untrimmed):
        try:
            print(f"Generating 5D data for {ticker} from 1D data...")
            df_5d = self._resample_to_5d(df_1d_untrimmed)
            df_5d = self._calculate_market_cycle(df_5d)
            self.save_data(ticker, '5D', df_5d)
        except Exception as e:
            print(f"Error generating 5D data for {ticker}: {e}")

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

    def save_data(self, ticker, timeframe, data, trim=True):
        if self.output == "firestore":
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
        else:
            if not os.path.exists('./data'):
                os.makedirs('./data')
            data.to_csv(f"./data/{ticker}_{timeframe}.csv")

    def _resample_to_5d(self, data):
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
        if self.output == "file":
            file_path = f"./data/{ticker}_{timeframe}.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                if trim and len(df) > self.max_datapoints:
                    df = df.iloc[-self.max_datapoints:]
                return df
            else:
                return None
        else:
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

    def tickerStatus(self, ticker, project=None):
        if self.output == "file":
            return False

        def get_status(ticker, timeframe, mc_field):
            data = self.get_data(ticker, timeframe, trim=False)
            data = data.replace(np.nan, None)
            if data is None or len(data) < 4:
                return {
                    "value": None,
                    "delta0": None,
                    "delta1": None
                }
            latest = data.iloc[-1][mc_field] if mc_field in data.columns else None
            previous = data.iloc[-2][mc_field] if mc_field in data.columns else None
            previous2 = data.iloc[-3][mc_field] if mc_field in data.columns else None
            previous3 = data.iloc[-4][mc_field] if mc_field in data.columns else None
            if latest is not None and previous is not None and previous2 is not None and previous3 is not None:
                delta0 = latest - previous
                delta1 = previous - previous2
                delta2 = previous2 - previous3
            else:
                delta0 = None
                delta1 = None
                delta2 = None
            return {
                "value": latest,
                "value1": previous,
                "value2": previous2,
                "value3": previous3,
                "delta0": delta0,
                "delta1": delta1,
                "delta2": delta2
            }

        doc_ref = self.db.collection(self.table).document(f"{ticker}_mc")
        doc = doc_ref.get()
        if not doc.exists:
            return None

        data = doc.to_dict().get('data', [])
        if len(data) < 3:
            return None

        latest_timestamp = doc.to_dict().get('latest_timestamp', None)
        last_10 = data[-10:]
        last_10 = json5.loads(json5.dumps(last_10).replace(': NaN', ': null'))
        last = data[-1]

        status = {
            "1min": get_status(ticker, "1min", 'marketCycle'),
            "1h": get_status(ticker, "1h", 'marketCycle'),
            "1d": get_status(ticker, "1D", 'marketCycle'),
            "5d": get_status(ticker, "5D", 'marketCycle')
        }

        result = {
            "ticker": ticker,
            "latest_timestamp": latest_timestamp,
            "last_10": last_10,
            "status": status
        }

        if project:
            position_doc_id = f"{project}-{ticker}"
            position_doc_ref = self.db.collection("trade_positions").document(position_doc_id)
            position_doc = position_doc_ref.get()
            if position_doc.exists:
                position = position_doc.to_dict()
                latest_close = last["Close"]
                gains = ((latest_close - position["avg_cost"]) / position["avg_cost"]) * 100 if latest_close else None
                position["gains"] = gains
                result["position"] = position

        return result
