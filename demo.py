from DataGetter import YfDataGetter, PolygonIoDataGetter
from DataCacher import FirestoreDataCacher, PklDataCacher
from DataExtender import DataExtender


# Download the data
dataGetter = PolygonIoDataGetter() # Use Yahoo Finance API
data = dataGetter.get(symbol="GME", since=date) # Get the 1min data since {date}, return a dataframe wil columns [Open, Close, High, Low, Volume] (rename to those names if neccessary), set a datetime index.

# Save the data
"""
    class DataCacher -> Global methods, default to storing data to csv files
    class FirestoreDataCacher(DataCacher) -> Extend DataCacher, replace the data source with Firestore instead of csv
    class PklDataCacher(DataCacher) -> Extend DataCacher, replace the data source with pandas pkl files instead of csv
"""
dataCacher = FirestoreDataCacher()
dataCacher.save(symbol="GME", data=data) # Save the data ensuring there are no 
data_1min = dataCacher.get(symbol="GME", since=date, timeframe="1min") # Original data
data_5min = dataCacher.get(symbol="GME", since=date, timeframe="5min") # get the 1min data and convert to 5min timeframe
data_30min = dataCacher.get(symbol="GME", since=date, timeframe="30min") # get the 1min data and convert to 30min timeframe
data_1h = dataCacher.get(symbol="GME", since=date, timeframe="1h") # get the 1min data and convert to 1h timeframe

# Add the extra columns & calculations
"""
    Add data columns to the pandas dataframe. Example: "MarketCycle" (fill with 0, I'll write the logic myself)
"""
dataExtender = DataExtender()
data_1min = dataExtender.extend(data_1min)
data_5min = dataExtender.extend(data_5min)
data_30min = dataExtender.extend(data_30min)
data_1h = dataExtender.extend(data_1h)

# Zip the timeframes
"""
    Takes in a list of dataframes representing the same data on multiple timeframes, and "zip" them into a single dataframe.
    Use 1st dataframe's datatime index, and for every row set the values from the timeframes at that time.
    Keep only the specified columns, renaming them `{column}_{timeframe}`
"""
data_zipped = dataExtender.zip_timeframes(
    data=[data_1min, data_5min, data_30min, data_1h],
    timeframes=["1min", "5min", "30min", "1h"],
    columns=["Close", "MarketCycle"]
)