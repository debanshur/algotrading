from fyers_api import fyersModel

from fyers_integration.auth.json_util import get_json_value
import time
from datetime import datetime as dt


def main():
    client_id = get_json_value('client_id')
    access_token = get_json_value('access_token')

    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,
                                  log_path="/Users/debanshu.rout/repo/external/algotrading/fyers_integration/data")

    symbol = {
        "symbols": "NSE:SBIN-EQ"
    }
    symbol = {
        "symbols": "NSE:TATAMOTORS-EQ"
    }
    print("%s,%s,%s,%s,%s,%s" % ("TimeStamp", "Name", "Token", "LTP", "Bid", "Ask"))

    # for x in range(200):
    while 0 < 10:
        time.sleep(1)
        response = fyers.quotes(data=symbol)
        # print(response)
        if response is not None and response['s'] == 'ok':
            data = response['d'][0]['v']
            ltp = data['lp']
            ask = data['ask']
            bid = data['bid']
            token = data['fyToken'][-4:]
            name = data['short_name']
            # t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['cmd']['t']))
            t = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            # print(data['cmd']['t'])
            print("%s,%s,%s,%.2f,%.2f,%.2f" % (t,name, token, ltp, bid, ask))
        else:
            print(f"Error : {response}")


if __name__ == '__main__':
    main()
