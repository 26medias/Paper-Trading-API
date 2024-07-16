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
        date = self.getDate(-80)
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

        return data_zipped

    def stats(self, symbol):
        data = self.get(symbol)
        output = {
            "status": {}
        }
        for timeframe in self.timeframes:
            mc_field = f"MarketCycle_{timeframe}"
            if timeframe == "1min":
                mc_field = "MarketCycle"
                data["Datetime"] = data.index
            latest = data.iloc[-1][mc_field] if mc_field in data.columns else None
            previous = data.iloc[-2][mc_field] if mc_field in data.columns else None
            previous2 = data.iloc[-3][mc_field] if mc_field in data.columns else None
            previous3 = data.iloc[-4][mc_field] if mc_field in data.columns else None
            #return (latest, previous, previous2, previous3)
            delta0 = latest - previous if latest and previous else None
            delta1 = previous - previous2 if latest and previous else None
            delta2 = previous2 - previous3 if latest and previous else None
            if timeframe == "1min":
                output["last_10"] = data.tail(10).to_dict('records')
            output["status"][timeframe] = {
                "value": latest,
                "value1": previous,
                "value2": previous2,
                "value3": previous3,
                "delta0": delta0,
                "delta1": delta1,
                "delta2": delta2
            }
        return output

#mc = MarketCycle()
#print(mc.get("AMC"))
#print(mc.stats("AMC"))