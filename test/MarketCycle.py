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
        data_5d = dataGetter.get(symbol=symbol, since=self.getDate(-120), timeframe="5d")

        data_1min = dataExtender.extend(data_1min)
        data_5min = dataExtender.extend(data_5min)
        data_30min = dataExtender.extend(data_30min)
        data_1h = dataExtender.extend(data_1h)
        data_1d = dataExtender.extend(data_1d)
        data_5d = dataExtender.extend(data_5d)

        #dataCacher.save(symbol, data_1min, "1min")
        #dataCacher.save(symbol, data_5min, "5min")
        #dataCacher.save(symbol, data_30min, "30min")
        #dataCacher.save(symbol, data_1h, "1h")
        #dataCacher.save(symbol, data_1d, "1d")
        #dataCacher.save(symbol, data_5d, "5d")

        data_zipped = dataExtender.zip_timeframes(
            data=[data_1min, data_5min, data_30min, data_1h, data_1d, data_5d],
            timeframes=self.timeframes,
            columns=["Close", "MarketCycle", "MarketCycle_1", "MarketCycle_2", "delta_0", "delta_1", "delta_2"]
        )
        #data_zipped = data_zipped.dropna()

        #dataCacher.save(symbol, data_zipped, "zipped")

        return data_zipped

    def renameDict(self, data, cols_from=[], cols_to=[]):
        #print("\n== renameDict ==")
        #print(data)
        #print(cols_from)
        #print(cols_to)
        if len(cols_from) != len(cols_to):
            raise ValueError("cols_from and cols_to must have the same length")

        # Convert to dictionary records
        records = data[cols_from].to_dict('records')

        # Rename columns
        renamed_records = [
            {cols_to[i]: record[cols_from[i]] for i in range(len(cols_from))}
            for record in records
        ]
        renamed_records = renamed_records[0]

        return renamed_records
    
    def stats(self, symbol):
        data = self.get(symbol).tail(1)
        data["Datetime"] = data.index
        output = {
            "ticker": symbol
        }
        cols0 = ["Datetime", "Open", "High", "Low", "Close"]
        cols = ["MarketCycle", "MarketCycle_1", "MarketCycle_2", "delta_0", "delta_1", "delta_2"]
        for timeframe in self.timeframes:
            if timeframe == '1min':
                output[timeframe] = data[cols0+cols].to_dict('records')[0]
            else:
                cols2 = [f"{item}_{timeframe}" for item in cols]
                output[timeframe] = self.renameDict(data, cols2, cols)
            
            """
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
            """
        return output

#mc = MarketCycle()
#print(mc.get("AMC"))
#print(mc.stats("AMC"))