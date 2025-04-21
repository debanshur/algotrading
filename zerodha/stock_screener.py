from kiteconnect import KiteConnect
from modules import auth
import pandas as pd

userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

dict = {}

def get_all_nse_instruments():
    data = kite.instruments(exchange="NSE")

    df = pd.DataFrame(columns=[ 'instrument_token','tradingsymbol','name'])
    df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
    if not df.empty:
        df = df[['instrument_token','tradingsymbol','name']]

    for ind in df.index:
        tokenName = df['tradingsymbol'][ind]
        tokenNumber = df['instrument_token'][ind]
        dict[tokenName] = tokenNumber


def isNaN(string):
    return string != string


def get_custom_instruments(stocks_list):
    get_all_nse_instruments()

    tokenNames = stocks_list.Symbol.values
    tokenNameList = []
    tokenNumberList = []

    for tokenName in tokenNames:
        if not isNaN(tokenName):
            tokenName = tokenName.strip()
            tokenNameList.append(tokenName)
            tokenNumberList.append(dict[tokenName])

    print("\nToken Name : \n",tokenNameList)
    print("\nToken Number : \n",tokenNumberList)


stocks_list = pd.read_csv("data.csv")
get_custom_instruments(stocks_list)
