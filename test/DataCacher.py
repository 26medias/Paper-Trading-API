import requests
import pandas as pd
import pickle
import os
from google.cloud import firestore


class DataCacher:
    def save(self, symbol, data):
        raise NotImplementedError("Subclasses should implement this!")

    def get(self, symbol, since, timeframe):
        raise NotImplementedError("Subclasses should implement this!")
    
    def convert_timeframe(self, df, timeframe):
        rule = {
            '1min': '1min',
            '5min': '5min',
            '30min': '30min',
            '1h': '1h',
            '1d': '1d',
            '5d': '5d'
        }

        if timeframe not in rule:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        if timeframe == "1min":
            return df
        else:
            df_resampled = df.resample(rule[timeframe]).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            return df_resampled

class FirestoreDataCacher(DataCacher):
    def __init__(self):
        self.db = firestore.Client()

    def save(self, symbol, data):
        collection_ref = self.db.collection(symbol)
        for index, row in data.iterrows():
            doc_ref = collection_ref.document(index.isoformat())
            doc_ref.set(row.to_dict())

    def get(self, symbol, since, timeframe):
        collection_ref = self.db.collection(symbol)
        docs = collection_ref.where('datetime', '>=', since).stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        return self.convert_timeframe(df, timeframe)


class PklDataCacher(DataCacher):
    def __init__(self, directory="data"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save(self, symbol, data):
        with open(f"{self.directory}/{symbol}.pkl", "wb") as f:
            pickle.dump(data, f)

    def get(self, symbol, since, timeframe):
        with open(f"{self.directory}/{symbol}.pkl", "rb") as f:
            data = pickle.load(f)
        data = data[data.index >= since]
        return self.convert_timeframe(data, timeframe)


class CsvDataCacher(DataCacher):
    def __init__(self, directory="data"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def savePrimary(self, symbol, data):
        data.to_csv(f"{self.directory}/{symbol}.csv")

    def save(self, symbol, data, timeframe):
        data.to_csv(f"{self.directory}/{symbol}_{timeframe}.csv")

    def read(self, symbol, timeframe):
        file_path = f"{self.directory}/{symbol}_{timeframe}.csv"
        if not os.path.exists(file_path):
            return None
        
        return pd.read_csv(file_path, index_col=0, parse_dates=True)

    def get(self, symbol, since, timeframe):
        file_path = f"{self.directory}/{symbol}.csv"
        if not os.path.exists(file_path):
            return None
        
        data = pd.read_csv(file_path, index_col=0, parse_dates=True)
        data = data[data.index >= since]
        return self.convert_timeframe(data, timeframe)
