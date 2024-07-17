import pandas as pd
import numpy as np


class HelperTA:
    def Stochastic(self, data, period=14):
        low = data.rolling(window=period, min_periods=1).min()
        high = data.rolling(window=period, min_periods=1).max()
        k_percent = 100 * ((data - low) / (high - low))
        return k_percent

    def RSI(self, data, period=14):
        delta = data.diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def stockRSI(self, data, K=5, D=5, rsiPeriod=20, stochPeriod=3):
        rsi = self.RSI(data, period=rsiPeriod).bfill()
        stoch = self.Stochastic(rsi, period=stochPeriod).bfill()
        k = stoch.rolling(window=K, min_periods=1).mean().bfill()
        d = k.rolling(window=D, min_periods=1).mean().bfill()
        return (k, d)

    def DCO(self, data, donchianPeriod=20, smaPeriod=3):
        lower = data.rolling(window=donchianPeriod).min()
        upper = data.rolling(window=donchianPeriod).max()
        DCO = (data - lower) / (upper - lower) * 100
        s = DCO.rolling(window=smaPeriod).mean()
        return (DCO, s)

    def MarketCycle(self, donchianPrice, rsiPrice, srsiPrice, donchianPeriod, donchianSmoothing, rsiPeriod, rsiSmoothing, srsiPeriod, srsiSmoothing, srsiK, srsiD, rsiWeight, srsiWeight, dcoWeight):
        DCO, DCOs = self.DCO(donchianPrice, donchianPeriod, donchianSmoothing)
        rsiValue = self.RSI(rsiPrice, rsiPeriod)
        rsiK = rsiValue.rolling(window=rsiSmoothing).mean()
        k, d = self.stockRSI(srsiPrice, srsiK, srsiD, srsiPeriod, srsiSmoothing)
        aggr = ((DCO + DCOs) * dcoWeight + (rsiValue + rsiK) * rsiWeight + (k + d) * srsiWeight) / (2 * (dcoWeight + rsiWeight + srsiWeight))
        return aggr

    
