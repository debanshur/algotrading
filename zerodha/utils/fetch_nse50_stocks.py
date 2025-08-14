import os
import sys

import pandas as pd
import requests
from kiteconnect import KiteConnect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import auth

userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])


# Step 1: Fetch NIFTY 50 symbols from NSE in index order
def fetch_nifty50_symbols():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {"User-Agent": "Mozilla/5.0"}
    session = requests.Session()
    session.headers.update(headers)
    session.get("https://www.nseindia.com")  # warm-up
    resp = session.get(url)
    resp.raise_for_status()
    data = resp.json()["data"]
    # Keep NSE order
    return [item["symbol"] for item in data]


# Step 2: Load Zerodha instrument list from URL
def load_instruments_from_url():
    instruments_url = "https://api.kite.trade/instruments"
    df = pd.read_csv(instruments_url)
    return df


# Step 3: Match NIFTY 50 symbols to tokens in the same order
def match_tokens_in_order(nifty_symbols, instruments_df):
    nse_instruments = instruments_df[instruments_df["exchange"] == "NSE"]
    tickerlist = []
    tokenlist = []
    for sym in nifty_symbols:
        row = nse_instruments[nse_instruments["tradingsymbol"] == sym]
        if not row.empty:
            tickerlist.append(sym)
            tokenlist.append(int(row.iloc[0]["instrument_token"]))
        else:
            tickerlist.append(sym)
            tokenlist.append(None)  # If token not found
    return tickerlist, tokenlist


if __name__ == "__main__":
    nifty_symbols = fetch_nifty50_symbols()
    instruments_df = load_instruments_from_url()
    tickerlist, tokenlist = match_tokens_in_order(nifty_symbols, instruments_df)

    print("tickerlist =", tickerlist)
    print("tokenlist  =", tokenlist)
    print("-----------------------------------")

    # Step 1: Build Zerodha instrument strings
    # Format: "<exchange>:<tradingsymbol>"
    instruments = [f"NSE:{symbol}" for symbol in tickerlist]

    # Step 2: Fetch live quotes from Zerodha
    quotes = kite.quote(instruments)

    # Step 3: Filter stocks with price > ₹3000
    low_price_tickers = []
    low_price_tokens = []

    for symbol, token in zip(tickerlist, tokenlist):
        ltp = quotes[f"NSE:{symbol}"]["last_price"]
        if ltp < 3500:
            low_price_tickers.append(symbol)
            low_price_tokens.append(token)

    # Step 4: Output
    print("tickerlist =", low_price_tickers)
    print("tokenlist  =", low_price_tokens)
