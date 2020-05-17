# Source : https://github.com/peerchemist/finta

def TP(df) :
        """Typical Price refers to the arithmetic average of the high, low, and closing prices for a given period."""
        df['TP'] = (df['high'] + df['low'] + df['close']) / 3
        return df

 
def calc(df, period = 14) :
    """The money flow index (MFI) is a momentum indicator that measures
    the inflow and outflow of money into a security over a specific period of time.
    MFI can be understood as RSI adjusted for volume.
    The money flow indicator is one of the more reliable indicators of overbought and oversold conditions, perhaps partly because
    it uses the higher readings of 80 and 20 as compared to the RSI's overbought/oversold readings of 70 and 30"""

    TP(df)
    df['rmf'] = df['TP'] * df['volume']    
    df["delta"] = df["TP"].diff()
    def pos(row):
        if row["delta"] > 0:
            return row['rmf']
        else:
            return 0

    def neg(row):
        if row["delta"] < 0:
            return row['rmf']
        else:
            return 0

    df["neg"] = df.apply(neg, axis=1)
    df["pos"] = df.apply(pos, axis=1)

    
    mfratio = df["pos"].rolling(window=period).sum() / df["neg"].rolling(window=period).sum()
    
    df["mfi"] = 100 - (100 / (1 + mfratio))
    df.drop(['rmf', 'pos', 'neg', 'delta', 'TP'], inplace=True, axis=1)
    return df