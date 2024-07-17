import pandas as pd

from HelperTA import HelperTA

class DataExtender:
    def extend(self, df):
        self.ta = HelperTA()
        data = df.copy()
        data = data.dropna()

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

        data['MarketCycle'] = self.ta.MarketCycle(donchianPrice, rsiPrice, srsiPrice, donchianPeriod, donchianSmoothing, rsiPeriod, rsiSmoothing, srsiPeriod, srsiSmoothing, srsiK, srsiD, rsiWeight, srsiWeight, dcoWeight)

        data['MarketCycle_1'] = data['MarketCycle'].shift(1)
        data['MarketCycle_2'] = data['MarketCycle'].shift(2)
        MarketCycle_3 = data['MarketCycle'].shift(3)
        data['delta_0'] = data['MarketCycle'] - data['MarketCycle_1']
        data['delta_1'] = data['MarketCycle_1'] - data['MarketCycle_2']
        data['delta_2'] = data['MarketCycle_2'] - MarketCycle_3
        return data

    def zip_timeframes(self, data, timeframes, columns):
        # Use the first DataFrame as the reference
        base_df = data[0].copy()
        
        for i, df in enumerate(data):
            if i == 0:
                continue
            df_reindexed = df.reindex(base_df.index, method='nearest')
            for col in columns:
                base_df[f"{col}_{timeframes[i]}"] = df_reindexed[col]
        
        return base_df