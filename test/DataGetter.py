import requests
import pandas as pd
import pickle
import os
from datetime import date
from datetime import datetime, timedelta

class DataGetter:
    def get(self, symbol, since):
        raise NotImplementedError("Subclasses should implement this!")

class PolygonIoDataGetter(DataGetter):
    def __init__(self, ):
        self.api_key = os.getenv('POLYGON_API_KEY')

    def getDate(self, days_ago):
        date = datetime.now() + timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")
    
    def get(self, symbol, since):
        today = date.today().strftime("%Y-%m-%d")
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{since}/{today}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": "50000",
            "apiKey": self.api_key
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "results" not in data:
            raise Exception("Failed to fetch data from Polygon.io API")

        df = pd.DataFrame(data["results"])
        df.rename(columns={"o": "Open", "c": "Close", "h": "High", "l": "Low", "v": "Volume", "t": "timestamp"}, inplace=True)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        df.drop(columns=['timestamp'], inplace=True)
        return df
    
