from DataGetter import PolygonIoDataGetter
from DataCacher import CsvDataCacher
from DataExtender import DataExtender
from datetime import datetime, timedelta

def getDate(days_ago):
    date = datetime.now() + timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")

# Example usage
dataGetter = PolygonIoDataGetter()  # Use Polygon.io API
date = getDate(-100)
print(date)

data = dataGetter.get(symbol="GME", since=date)  # Get the 1min data since {date}

print("Got data")
print(data)

dataCacher = CsvDataCacher()
dataCacher.savePrimary(symbol="GME", data=data)

print("Saved data")

data_1min = dataCacher.get(symbol="GME", since=date, timeframe="1min")
data_5min = dataCacher.get(symbol="GME", since=date, timeframe="5min")
data_30min = dataCacher.get(symbol="GME", since=date, timeframe="30min")
data_1h = dataCacher.get(symbol="GME", since=date, timeframe="1h")
data_1d = dataCacher.get(symbol="GME", since=date, timeframe="1d")
data_5d = dataCacher.get(symbol="GME", since=date, timeframe="5d")

dataCacher.save(symbol="GME", data=data_1min, timeframe="1min")
dataCacher.save(symbol="GME", data=data_5min, timeframe="5min")
dataCacher.save(symbol="GME", data=data_30min, timeframe="30min")
dataCacher.save(symbol="GME", data=data_1h, timeframe="1h")
dataCacher.save(symbol="GME", data=data_1d, timeframe="1d")
dataCacher.save(symbol="GME", data=data_5d, timeframe="5d")

dataExtender = DataExtender()
data_1min = dataExtender.extend(data_1min)
data_5min = dataExtender.extend(data_5min)
data_30min = dataExtender.extend(data_30min)
data_1h = dataExtender.extend(data_1h)
data_1d = dataExtender.extend(data_1d)
data_5d = dataExtender.extend(data_5d)

dataCacher.save(symbol="GME", data=data_1min, timeframe="1min_mc")
dataCacher.save(symbol="GME", data=data_5min, timeframe="5min_mc")
dataCacher.save(symbol="GME", data=data_30min, timeframe="30min_mc")
dataCacher.save(symbol="GME", data=data_1h, timeframe="1h_mc")
dataCacher.save(symbol="GME", data=data_1d, timeframe="1d_mc")
dataCacher.save(symbol="GME", data=data_5d, timeframe="5d_mc")

print("Extended data")

data_zipped = dataExtender.zip_timeframes(
    data=[data_1min, data_5min, data_30min, data_1h, data_1d, data_5d],
    timeframes=["1min", "5min", "30min", "1h", "1d", "5d"],
    columns=["Close", "MarketCycle"]
)
print("Zipped data")

dataCacher.save(symbol="GME", data=data_zipped, timeframe="zipped")

print(data_zipped)