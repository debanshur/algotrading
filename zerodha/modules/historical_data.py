import pandas as pd

def get(kite, token, startdate, enddate, interval):
    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    try:
        data = kite.historical_data(token, startdate, enddate, interval)
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        #print(df)
        if not df.empty:
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df['date'] = df['date'].astype(str).str[:-6]
            df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        print("******* ERROR Fetching Historical Data ********", token, e)
    return df