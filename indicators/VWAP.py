import numpy as np
import pandas as pd

def TP(df) :
    """Typical Price refers to the arithmetic average of the high, low, and closing prices for a given period."""
    df['TP'] = (df['high'] + df['low'] + df['close']) / 3
    return df


def vwap(df):
    """
        The volume weighted average price (VWAP) is a trading benchmark used especially in pension plans.
        VWAP is calculated by adding up the dollars traded for every transaction (price multiplied by number of shares traded) and then dividing
        by the total shares traded for the day.
    """
    df['vwap'] = np.cumsum(df['volume'] * df['TP']) / np.cumsum(df['volume'])
    return df


def calc(df):
    TP(df)
    df[['intraday','time']] = df['date'].astype(str).str.split(expand=True) 
    df = df.groupby(df['intraday'], group_keys=False).apply(vwap) 
    df.drop(['TP', 'intraday', 'time'], inplace=True, axis=1)
    return df
        
