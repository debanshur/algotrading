from kiteconnect import KiteConnect
from math import floor, ceil
import datetime
import pandas as pd
import numpy as np
import sys
import os
import time

from modules import auth
from modules import historical_data
from indicators import SuperTrend, MACD, RSI

risk_per_trade = 100 # Stoploss amount
supertrend_period = 10
supertrend_multiplier=3
candlesize = '10minute'
one_hour_rsi = 50
orderslist = {}

#pd.set_option('display.max_columns',50)
pd.set_option('display.max_rows', None)
print("\n******** Started ********* : ", datetime.datetime.now())

"""
1. Login to kite
"""
userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])
    
print("******** UserData Loaded ********* : ", datetime.datetime.now())

#list all tickers you want to trade
tickerlist = ["BAJAJFINSV","ZEEL","HDFCBANK","LT","HDFC","ICICIBANK","LICHSGFIN","CENTURYTEX","SBIN","INDUSINDBK","TATASTEEL","RELIANCE","MARUTI","VEDL","AXISBANK","TATAMOTORS","SIEMENS","TATAMTRDVR","DLF","HINDALCO","M&M","ULTRACEMCO","TATACHEM","L&TFH","AMBUJACEM","UNIONBANK","CANBK","BANKINDIA","VOLTAS","TATAPOWER","GODREJIND","BAJAJ-AUTO","APOLLOTYRE","NCC","RECLTD","BHARATFORG","TATAGLOBAL","PFC","ACC","JSWSTEEL","M&MFIN","BHEL","HEROMOTOCO","ASHOKLEY","BANKBARODA","JINDALSTEL","SRF","ASIANPAINT","UPL","EXIDEIND","ONGC"]
#tickerlist = ["HDFCBANK","LT","HDFC","ICICIBANK","LICHSGFIN","CENTURYTEX","SBIN","INDUSINDBK","TATASTEEL","RELIANCE"]
#tickerlist = ["BAJAJFINSV"]
tokenlist = [4268801,975873,341249,2939649,340481,1270529,511233,160001,779521,1346049,895745,738561,2815745,784129,1510401,884737,806401,4343041,3771393,348929,519937,2952193,871681,6386689,325121,2752769,2763265,1214721,951809,877057,2796801,4267265,41729,593665,3930881,108033,878593,3660545,5633,3001089,3400961,112129,345089,54273,1195009,1723649,837889,60417,2889473,173057,633601]
#tokenlist = [341249,2939649,340481,1270529,511233,160001,779521,1346049,895745,738561]
#tokenlist = [4268801]


def compute_data(token):
    global one_hour_rsi
    #enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(3)
    try:
        df = historical_data.get(kite, token, startdate, enddate, candlesize)
        df = SuperTrend.calc(df, supertrend_period, supertrend_multiplier)
        df = MACD.calc(df)
        rsi = historical_data.get(kite, token, startdate, enddate, "60minute")
        rsi = RSI.calc(rsi)
        one_hour_rsi = rsi.RSI_14.values[-1]
    except Exception as e:
        print("******* ERROR Computing Historical Data ********", token, e)
    return df

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
    for i in range(0, len(tickerlist)):

        if (tickerlist[i] in orderslist):
            continue
        try:
            histdata = compute_data(tokenlist[i])
            #print(histdata)
            super_trend = histdata.STX.values

            high = histdata.high.values[-2]
            low = histdata.low.values[-2]
            macd = histdata.hist_12_26_9.values[-2]
            stoploss_buy =  histdata.ST.values[-2]#histdata.low.values[-3] # third last candle as stoploss
            stoploss_sell = histdata.ST.values[-2] # third last candle as stoploss

            volume = histdata.volume.values[-2]
            has_volume = check_volume(histdata.open.values[-2], volume)


            #if stoploss_buy > lastclose * 0.996:
                #stoploss_buy = lastclose * 0.996 # minimum stoploss as 0.4 %

            #if stoploss_sell < lastclose * 1.004:
                #stoploss_sell = lastclose * 1.004 # minimum stoploss as 0.4 %
            #print("lastclose",lastclose)
            #print("stoploss abs",stoploss)
            print(tickerlist[i],high,low,super_trend[-4:],round(macd,4),int(one_hour_rsi), volume)

            if super_trend[-1]=='up' and super_trend[-2]=='up' and super_trend[-3]=='down' and super_trend[-4]=='down' \
                                    and macd>0 and one_hour_rsi > 50:
                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue

                stoploss_buy = high - stoploss_buy
                #print("stoploss delta", stoploss)

                quantity = 1#floor(max(1, (risk_per_trade/stoploss_buy)))
                target = stoploss_buy*2 # risk reward as 3

                price = high + (0.05*high)/100
                #print(price)
                #price = int(ceil(price))
                price = int(100 * (ceil(price / 0.05) * 0.05)) / 100
                stoploss_buy = int(100 * (floor(stoploss_buy / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100

                orderslist[tickerlist[i]] = price - stoploss_buy
                #print(price)
                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="BUY",
                                             quantity=quantity,
                                             trigger_price=price,
                                             product='MIS',
                                             order_type='SL-M',
                                             validity='DAY',
                                             variety="regular"
                                             )
                
                print("         Order : ", "BUY", tickerlist[i], "high : ", high,"quantity:",quantity, "price:",price,datetime.datetime.now())

            if super_trend[-1]=='down' and super_trend[-2]=='down' and super_trend[-3]=='up' and super_trend[-4]=='up' \
                                        and macd<0 and one_hour_rsi < 50:

                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue

                stoploss_sell= stoploss_sell - low
                #print("stoploss delta", stoploss)

                quantity = 1#floor(max(1, (risk_per_trade/stoploss_sell)))
                target = stoploss_sell*2 # risk reward as 3

                price = low - (0.05*low)/100
                #price = int(floor(price))
                price = int(100 * (floor(price / 0.05) * 0.05)) / 100
                stoploss_sell = int(100 * (floor(stoploss_sell / 0.05) * 0.05)) / 100
                quantity = int(quantity)
                target = int(100 * (floor(target / 0.05) * 0.05)) / 100

                orderslist[tickerlist[i]] = price + stoploss_sell
                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="SELL",
                                             quantity=quantity,
                                             trigger_price=price,
                                             product='MIS',
                                             order_type='SL-M',
                                             validity='DAY',
                                             variety="regular"
                                             )
                print("         Order : ", "SELL", tickerlist[i],"low : ", low,"quantity:",quantity, "price:",price, datetime.datetime.now())

        except Exception as e :
            print(e)

def check_order_status1():
    global orderslist
    df = pd.DataFrame(columns=['order_id', 'status', 'tradingsymbol', 'instrument_token', 'transaction_type', 'quantity'])
    try:
        data = kite.orders()
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        #print(df)
        if not df.empty:
            df = df[['order_id', 'status', 'tradingsymbol', 'instrument_token', 'transaction_type', 'quantity']]
    except Exception as e:
        print("******* ERROR Fetching Historical Data ********", e)
    for ind in df.index:
        token = df['tradingsymbol'][ind]
        if token in orderslist:
            orderslist.pop(token) 
        else:
            orderslist[token] = "0"
        #print(df['tradingsymbol'][ind], df['transaction_type'][ind]) 

    print(orderslist)
    return df


def check_order_status():
    global orderslist
    df = pd.DataFrame(columns=['order_id', 'status', 'tradingsymbol', 'instrument_token', 'transaction_type', 'quantity'])
    try:
        data = kite.orders()
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
    global runcount
    start_time = int(9) * 60 + int(25)  # specify in int (hr) and int (min) foramte
    end_time = int(15) * 60 + int(10)  # do not place fresh order
    stop_time = int(15) * 60 + int(15)  # square off all open positions
    last_time = start_time
    schedule_interval = 60  # run at every 1 min
    #runcount = 0
    check_order_status()
    while True:
        if (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= end_time:
            if (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= stop_time:
                print("***** Trading day closed *****")
                break

        elif (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= start_time:
            if time.time() >= last_time:
                last_time = time.time() + schedule_interval
                print("\n\n {} Run Count : Time - {} ".format(runcount, datetime.datetime.now()))
                if runcount >= 0:
                    try:    
                        run_strategy()
                    except Exception as e:
                        print("******* Run Error *********", e)
                runcount = runcount + 1
        else:
            print('****** Waiting ********', datetime.datetime.now())
            time.sleep(1)

runcount = 0
run()
