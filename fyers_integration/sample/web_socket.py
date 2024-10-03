from fyers_api.Websocket import ws

from fyers_integration.auth.json_util import get_json_value
from time import strftime, localtime


def run_process_foreground_symbol_data(access_token):
    '''This function is used for running the symbolData in foreground
    1. log_path here is configurable this specifies where the output will be stored for you
    2. data_type == symbolData this specfies while using this function you will be able to connect to symbolwebsocket to get the symbolData
    3. run_background = False specifies that the process will be running in foreground'''
    data_type = "symbolData"
    # symbol = ["NSE:SBIN-EQ","NSE:ONGC-EQ"]   ##NSE,BSE sample symbols
    # symbol = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX", "NSE:SBIN-EQ", "NSE:HDFC-EQ", "NSE:IOC-EQ"]
    symbol = ["NSE:SBIN-EQ"]
    # symbol =["MCX:SILVERMIC21NOVFUT","MCX:GOLDPETAL21SEPTFUT"]
    fs = ws.FyersSocket(access_token=access_token, run_background=False, log_path="/Users/debanshu.rout/repo/external/algotrading/fyers_integration/data")
    fs.websocket_data = custom_message
    fs.subscribe(symbol=symbol, data_type=data_type)
    fs.keep_running()
    # unsubscribe_symbol = ["NSE:SBIN-EQ"]
    # fs.unsubscribe(symbol=unsubscribe_symbol)


def custom_message(msg):
    print(f"Custom:{msg}")

    print(strftime('%Y-%m-%d %H:%M:%S', localtime(msg[0]['timestamp'])))
    print(msg[0]['market_pic'])


def main():
    ### Insert the accessToken and app_id over here in the following format (APP_ID:access_token)
    token = get_json_value('access_token')
    client = get_json_value('client_id')
    access_token = client + ":" + token

    ## run a specific process you need to connect to get the updates on
    run_process_foreground_symbol_data(access_token)


if __name__ == '__main__':
    main()