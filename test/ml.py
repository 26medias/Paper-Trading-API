from DataGetter import PolygonIoDataGetter
from DataCacher import CsvDataCacher
from DataExtender import DataExtender
from datetime import datetime, timedelta

dataGetter = PolygonIoDataGetter()
dataCacher = CsvDataCacher()
dataExtender = DataExtender()

class MarketCycle:
    timeframes = ["1min", "5min", "30min", "1h", "1d", "5d"]

    def getDate(self, days_ago):
        date = datetime.now() + timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")
    
    def get(self, symbol):
        date = self.getDate(-10000)
        data = dataGetter.get(symbol=symbol, since=date)

        data_1min = data
        data_5min = dataCacher.convert_timeframe(data, "5min")
        data_30min = dataCacher.convert_timeframe(data, "30min")
        data_1h = dataCacher.convert_timeframe(data, "1h")
        data_1d = dataCacher.convert_timeframe(data, "1d")
        data_5d = dataCacher.convert_timeframe(data, "5d")

        data_1min = dataExtender.extend(data_1min)
        data_5min = dataExtender.extend(data_5min)
        data_30min = dataExtender.extend(data_30min)
        data_1h = dataExtender.extend(data_1h)
        data_1d = dataExtender.extend(data_1d)
        data_5d = dataExtender.extend(data_5d)

        data_zipped = dataExtender.zip_timeframes(
            data=[data_1min, data_5min, data_30min, data_1h, data_1d, data_5d],
            timeframes=self.timeframes,
            columns=["Close", "MarketCycle"]
        )
        data_zipped = data_zipped.dropna()

        dataCacher.save(symbol, data_zipped, "mc")

        return data_zipped
    

    def percent(self, start, end):
        return (end-start)/start*100
    
    def minMax(self, df, range):
        _max = self.percent(df["Close"], df["High"].rolling(range).max().shift(-(range+1)))
        _min = self.percent(df["Close"], df["Low"].rolling(range).min().shift(-(range+1)))
        #df[f"max_{range}"] = self.percent(df["Close"], df["High"].rolling(range).max().shift(-(range+1)))
        #df[f"min_{range}"] = self.percent(df["Close"], df["Low"].rolling(range).min().shift(-(range+1)))
        df[f"mean_{range}"] = (_max + _min) / 2
        return df


    def process(self, symbol):
        data = dataCacher.read(symbol, "mc")
        ranges = [5, 10, 20, 60]
        for range in ranges:
            data = self.minMax(data, range)
        dataCacher.save(symbol, data, "ml")
        return data

mc = MarketCycle()
#print(mc.get("GME"))
print(mc.process("GME").head(20))

