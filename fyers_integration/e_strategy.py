import time
from math import floor, ceil
import pandas as pd
import requests
from fyers_api import accessToken, fyersModel




from fyers_integration.util import get_historical_data
from indicators import SuperTrend, EMA, MACD, RSI, MFI, VWAP
import datetime

from auth.json_util import get_json_value

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)


access_token = get_json_value('access_token')
client_id = "TC8P3VH4H7-100"
fyers = fyersModel.FyersModel(token=access_token, is_async=False, client_id=client_id, log_path="/Users/debanshu.rout/repo/external/algotrading/log")
#print(fyers.get_profile()['data']['name'])

run_count = 0
exit_count = 0
supertrend_period = 10
supertrend_multiplier=3
orderslist = {}
time_frame = "10"
one_hour_rsi = 50

stockList = ["NSE:RELIANCE-EQ", "NSE:SBIN-EQ"]


def compute_data(stock):
    global one_hour_rsi
    #enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(5)

    try:
        df = get_historical_data(fyers, stock, time_frame, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        df = EMA.calc(df, 'close', 'ema_5', 5)
        #df = EMA.calc(df, 'close', 'ema_20', 20)
        #df = MACD.calc(df)
        #df = MFI.calc(df)
        #df = VWAP.calc(df)

        #df = SuperTrend.calc(df, supertrend_period, supertrend_multiplier)
        #rsi = get_historical_data(fyers, stock, "60", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        #rsi = RSI.calc(rsi)
        #one_hour_rsi = rsi.RSI_14.values[-1]

        print(df)
    except Exception as e:
        print("******* ERROR Computing Historical Data ********", e)
    return df


#
# ## Quotes
#
# data = {"symbols": "NSE:SBIN-EQ"}
# print(fyers.quotes(data))
# #
# # ## Market Depth
# #
# data = {"symbol": "NSE:SBIN-EQ", "ohlcv_flag": "1"}
# print(fyers.depth(data))

def check_volume(open, volume):
    if open <= 400 and volume >= 1000000:
        return True
    elif open > 400 and open <=700 and volume >= 500000:
        return True
    elif open > 700 and open <=1000 and volume >= 300000:
        return True
    elif open > 1000 and volume >= 100000:
        return True
    else:
        return False

def run_strategy():
    global orderslist
    global one_hour_rsi
    for i in range(0, len(stockList)):
        if stockList[i] in orderslist:
            continue
        try:
            histdata = compute_data(stockList[i])
            # print(histdata)
            super_trend = histdata.STX.values

            high = histdata.high.values[-2]
            low = histdata.low.values[-2]
            macd = histdata.hist_12_26_9.values[-2]
            stoploss_buy = histdata.ST.values[-2]  # histdata.low.values[-3] # third last candle as stoploss
            stoploss_sell = histdata.ST.values[-2]  # third last candle as stoploss

            volume = histdata.volume.values[-2]
            has_volume = check_volume(histdata.open.values[-2], volume)

            # if stoploss_buy > lastclose * 0.996:
            # stoploss_buy = lastclose * 0.996 # minimum stoploss as 0.4 %

            # if stoploss_sell < lastclose * 1.004:
            # stoploss_sell = lastclose * 1.004 # minimum stoploss as 0.4 %
            # print("lastclose",lastclose)
            # print("stoploss abs",stoploss)

            print(stockList[i], high, low, super_trend[-4:], round(macd, 4), int(one_hour_rsi), volume)

            if not has_volume:
                print("Sorry, Volume is low")
                continue

            if super_trend[-1] == 'up' and super_trend[-2] == 'up' and super_trend[-3] == 'down' and super_trend[
                -4] == 'down' \
                    and macd > 0 and one_hour_rsi > 50:

                stoploss_buy = high - stoploss_buy
                # print("stoploss delta", stoploss)

                quantity = 1  # floor(max(1, (risk_per_trade/stoploss_buy)))
                target = stoploss_buy * 2  # risk reward as 3

                price = high + (0.05 * high) / 100
                # print(price)
                # price = int(ceil(price))
                price = int(100 * (ceil(price / 0.05) * 0.05)) / 100
                stoploss_buy = int(100 * (floor(stoploss_buy / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100

                #orderslist[stockList[i]] = price - stoploss_buy
                # print(price)

                data = {
                    "symbol": stockList[i],
                    "qty": quantity,
                    "type": 3,
                    "side": 1,
                    "productType": "INTRADAY",
                    "limitPrice": 0,
                    "stopPrice": stoploss_buy,
                    "validity": "DAY",
                    "disclosedQty": 0,
                    "offlineOrder": "False",
                    "stopLoss": 0,
                    "takeProfit": 0
                }

                print(fyers.place_order(data))

                print("         Order : ", "BUY", stockList[i], "high : ", high, "quantity:", quantity, "price:",
                      price, datetime.datetime.now())

            if super_trend[-1] == 'down' and super_trend[-2] == 'down' and super_trend[-3] == 'up' and super_trend[
                -4] == 'up' \
                    and macd < 0 and one_hour_rsi < 50:

                if not has_volume:
                    print("Sorry, Volume is low")
                    # continue

                stoploss_sell = stoploss_sell - low
                # print("stoploss delta", stoploss)

                quantity = 1  # floor(max(1, (risk_per_trade/stoploss_sell)))
                target = stoploss_sell * 2  # risk reward as 3

                price = low - (0.05 * low) / 100
                # price = int(floor(price))
                price = int(100 * (floor(price / 0.05) * 0.05)) / 100
                stoploss_sell = int(100 * (floor(stoploss_sell / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100

                #orderslist[stockList[i]] = price + stoploss_sell

                data = {
                    "symbol": stockList[i],
                    "qty": quantity,
                    "type": 3,
                    "side": -1,
                    "productType": "INTRADAY",
                    "limitPrice": 0,
                    "stopPrice": stoploss_sell,
                    "validity": "DAY",
                    "disclosedQty": 0,
                    "offlineOrder": "False",
                    "stopLoss": 0,
                    "takeProfit": 0
                }

                print(fyers.place_order(data))

                print("         Order : ", "SELL", stockList[i], "low : ", low, "quantity:", quantity, "price:", price,
                      datetime.datetime.now())

        except Exception as e:
            print(e)


def check_order_status():
    global orderslist
    df = pd.DataFrame(columns=['order_id', 'status', 'tradingsymbol', 'instrument_token', 'transaction_type', 'quantity'])
    try:
        data = fyers.get_orders()
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        #print(df)
        if not df.empty:
            df = df[['order_id', 'status', 'tradingsymbol', 'instrument_token', 'transaction_type', 'quantity']]
    except Exception as e:
        print("******* ERROR Fetching Historical Data ********", e)
    for ind in df.index:
        token = df['tradingsymbol'][ind]
        orderslist[token] = "0"
        #print(df['tradingsymbol'][ind], df['transaction_type'][ind])

    print(orderslist)
    return df


def run():
    global run_count
    global exit_count
    trade_start_time = int(11) * 60 + int(25)  # specify in int (hr) and int (min) format
    order_end_time = int(14) * 60 + int(55)  # do not place fresh order
    square_off_time = int(15) * 60 + int(15)  # square off all open positions
    prev_time = trade_start_time
    schedule_interval = 60  # run at every 1 min
    #runcount = 0
    #check_order_status()

    next_time = trade_start_time

    # set next_time to the nearest 5th minute of current time
    if (datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5))) % 10 == 0:
        next_time = datetime.datetime.now().hour * 60 + \
                    ((datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5))) + 5)

    else:
        next_time = datetime.datetime.now().hour * 60 + \
                    (datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5)))

    while True:
        curr_time = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
        #check_order_status()
        if curr_time >= square_off_time:
            #close_positions()
            print("***** Trading Day closed *****")
            break
        if curr_time >= trade_start_time:
            if next_time <= curr_time < order_end_time:
                next_time = curr_time + 10
                time.sleep(2)
                print("\n\n {} Run Count : Time - {} ".format(run_count, datetime.datetime.now()))
                if run_count >= 0:
                    try:
                        run_strategy()
                    except Exception as e:
                        print("******* Run Error *********", e)
                run_count = run_count + 1

            if curr_time >= order_end_time and curr_time >= next_time:
                next_time = curr_time + 5
                time.sleep(2)
                print("\n\n {} Exit Count : Time - {} ".format(exit_count, datetime.datetime.now()))
                if exit_count >= 0:
                    try:
                        check_order_status()
                    except Exception as e:
                        print("******* Run Error *********", e)
                exit_count = exit_count + 1

        else:
            print('****** Waiting ********', datetime.datetime.now())
            time.sleep(1)


if __name__ == '__main__':
    #run()
    compute_data('NSE:SBIN-EQ')
    #print(fyers.tradebook())  ## This will provide all the trade related information

    #print(fyers.orderbook())  ## This will provide the user with all the order realted information

    #print(fyers.positions())