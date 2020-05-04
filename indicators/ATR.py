from indicators import EMA

def calc(df, period, ohlc=['open', 'high', 'low', 'close']):
    """
    Function to compute Average True Range (ATR)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])

    Returns :
        df : Pandas DataFrame with new columns added for
            True Range (TR)
            ATR (ATR_$period)
    """
    atr = 'ATR_' + str(period)

    # Compute true range only if it is not computed and stored earlier in the df
    if not 'TR' in df.columns:
        df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
        df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
        df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

        df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)

        df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    EMA.calc(df, 'TR', atr, period, alpha=True)

    return df