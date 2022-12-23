import pandas as pd


# data = {"symbol": "NSE:SBIN-EQ", "resolution": "D", "date_format": "1", "range_from": "2022-07-18",
#         "range_to": "2022-07-24", "cont_flag": "1"}


def get_historical_data(fyers, symbol, time_frame, start_date, end_date):
    data = {'symbol': symbol, 'resolution': time_frame, 'date_format': "1", 'range_from': start_date,
            'range_to': end_date,
            'cont_flag': "1"}

    data = fyers.history(data)['candles']
    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])

    try:
        df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'], dtype=None)
        # print(df)
        if not df.empty:
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df['date'] = pd.to_datetime(df['date'], unit='s', utc=True)
            # df['date'] = df['date'].dt.tz_localize('UTC')
            df['date'] = df['date'].dt.tz_convert('Asia/Kolkata')
            df['date'] = df['date'].astype(str).str[:-6]

            # df['date'] = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(df['date']))
            # df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        print("******* ERROR Fetching Historical Data ********", e)
    df.reset_index(drop=True)
    return df
