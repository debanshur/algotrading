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
from indicators import MACD, RSI, EMA, MFI, VWAP

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
tickerlist = ["RELIANCE"]
tokenlist = [738561]

#F&O nse 100
#tickerlist = ['BAJAJFINSV', 'BRITANNIA', 'ULTRACEMCO', 'BAJFINANCE', 'SRF', 'DRREDDY', 'BAJAJ-AUTO', 'NAUKRI', 'HINDUNILVR', 'ASIANPAINT', 'HDFC', 'HEROMOTOCO', 'TCS', 'NIITTECH', 'DIVISLAB', 'KOTAKBANK', 'PVR', 'TORNTPHARM', 'APOLLOHOSP', 'ACC', 'INDIGO', 'RELIANCE', 'JUBLFOOD', 'PIDILITIND', 'BATAINDIA', 'HDFCBANK', 'PEL', 'LT', 'SIEMENS', 'MGL', 'GODREJPROP', 'SRTRANSFIN', 'COLPAL', 'UBL', 'MUTHOOTFIN', 'TITAN', 'SBILIFE', 'MINDTREE', 'BALKRISIND', 'INDUSINDBK', 'LUPIN', 'RAMCOCEM', 'GRASIM', 'GODREJCP', 'AMARAJABAT', 'HAVELLS', 'VOLTAS', 'BERGEPAINT', 'ESCORTS', 'HDFCLIFE', 'INFY', 'TECHM', 'CUMMINSIND', 'AXISBANK', 'DABUR', 'MCDOWELL-N', 'CIPLA', 'MFSL', 'AUROPHARMA', 'UPL', 'ICICIBANK', 'IGL', 'CENTURYTEX', 'HCLTECH', 'SUNPHARMA', 'JUSTDIAL', 'M&M', 'TVSMOTOR', 'BHARATFORG', 'ICICIPRULI', 'SUNTV', 'CONCOR', 'TATASTEEL', 'BPCL', 'BANDHANBNK', 'BHARTIARTL', 'LICHSGFIN', 'MARICO', 'TATACHEM', 'M&MFIN', 'CADILAHC', 'UJJIVAN', 'BIOCON', 'GLENMARK', 'ADANIPORTS', 'CHOLAFIN', 'RBLBANK', 'HINDPETRO', 'JSWSTEEL', 'TATACONSUM', 'INFRATEL', 'AMBUJACEM', 'PETRONET', 'SBIN', 'TORNTPOWER', 'ZEEL', 'IBULHSGFIN', 'WIPRO', 'ITC', 'DLF']
#tokenlist = [4268801, 140033, 2952193, 81153, 837889, 225537, 4267265, 3520257, 356865, 60417, 340481, 345089, 2953217, 2955009, 2800641, 492033, 3365633, 900609, 40193, 5633, 2865921, 738561, 4632577, 681985, 94977, 341249, 617473, 2939649, 806401, 4488705, 4576001, 1102337, 3876097, 4278529, 6054401, 897537, 5582849, 3675137, 85761, 1346049, 2672641, 523009, 315393, 2585345, 25601, 2513665, 951809, 103425, 245249, 119553, 408065, 3465729, 486657, 1510401, 197633, 2674433, 177665, 548353, 70401, 2889473, 1270529, 2883073, 160001, 1850625, 857857, 7670273, 519937, 2170625, 108033, 4774913, 3431425, 1215745, 895745, 134657, 579329, 2714625, 511233, 1041153, 871681, 3400961, 2029825, 4369665, 2911489, 1895937, 3861249, 175361, 4708097, 359937, 3001089, 878593, 7458561, 325121, 2905857, 779521, 3529217, 975873, 7712001, 969473, 424961, 3771393]

#nifty50
#tickerlist = ['BAJAJ-AUTO', 'BAJFINANCE', 'HEROMOTOCO', 'HINDUNILVR', 'TCS', 'HDFC', 'ASIANPAINT', 'RELIANCE', 'KOTAKBANK', 'HDFCBANK', 'LT', 'TITAN', 'INFY', 'CIPLA', 'BHARTIARTL', 'TECHM', 'HCLTECH', 'GRASIM', 'SUNPHARMA', 'INDUSINDBK', 'AXISBANK', 'M&M', 'UPL', 'ICICIBANK', 'BPCL', 'ADANIPORTS', 'TATASTEEL', 'INFRATEL', 'WIPRO', 'JSWSTEEL', 'SBIN', 'ITC', 'POWERGRID', 'ZEEL', 'COALINDIA', 'HINDALCO']
#tokenlist = [4267265, 81153, 345089, 356865, 2953217, 340481, 60417, 738561, 492033, 341249, 2939649, 897537, 408065, 177665, 2714625, 3465729, 1850625, 315393, 857857, 1346049, 1510401, 519937, 2889473, 1270529, 134657, 3861249, 895745, 7458561, 969473, 3001089, 779521, 424961, 3834113, 975873, 5215745, 348929]


def compute_data(token):
    global one_hour_rsi
    #enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(15)
    try:
        df = historical_data.get(kite, token, startdate, enddate, candlesize)
        df = EMA.calc(df,'close','ema_5',5)
        df = EMA.calc(df,'close','ema_20',20)
        df = MACD.calc(df)
        df = MFI.calc(df)
        df = VWAP.calc(df)
        rsi = historical_data.get(kite, token, startdate, enddate, "60minute")
        rsi = RSI.calc(rsi)
        one_hour_rsi = rsi.RSI_14.values[-2]
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
            print(histdata)
            pre_ema5 = histdata.ema_5.values[-3]
            pre_ema20 = histdata.ema_20.values[-3]
            pre_close = histdata.close.values[-3]

            ema5 = histdata.ema_5.values[-2]
            ema20 = histdata.ema_20.values[-2]
            macd = histdata.hist_12_26_9.values[-2]
            mfi = histdata.mfi.values[-2]
            vwap = histdata.vwap.values[-2]

            open = histdata.open.values[-2]
            close = histdata.close.values[-2]
            high = histdata.high.values[-2]
            low = histdata.low.values[-2]
            
            volume = histdata.volume.values[-2]
            has_volume = check_volume(histdata.open.values[-2], volume)

            perc_change = ((close - pre_close) * 100) / open

            #print("-----------------------------------------------------------------------------------------")
            print(tickerlist[i],open,close,"::::",round(ema5,2),round(ema20,2),round(macd,4),int(mfi),int(one_hour_rsi),round(vwap,2),round(perc_change,2),volume)

            if (ema5 > ema20) and (pre_ema5 < pre_ema20) and (macd > 0) and (close > vwap):
                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue
                
                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (2500/high)))

                #orderslist[tickerlist[i]] = close

                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="BUY",
                                             quantity=quantity,
                                             product='MIS',
                                             order_type='MARKET',
                                             validity='DAY',
                                             variety="regular"
                                             )
                
                print("         Order : ","BUY",tickerlist[i],"quantity:",quantity,"price:",close,"rsi_1hour:",one_hour_rsi,"volume:",volume,datetime.datetime.now())

            if (ema5 < ema20) and (pre_ema5 > pre_ema20) and (macd < 0) and (close < vwap):
                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue

                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (2500/high)))

                #orderslist[tickerlist[i]] = close

                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="SELL",
                                             quantity=quantity,
                                             product='MIS',
                                             order_type='MARKET',
                                             validity='DAY',
                                             variety="regular"
                                             )
                
                print("         Order : ","SELL",tickerlist[i],"quantity:",quantity,"price:",close,"rsi_1hour:",one_hour_rsi,"volume:",volume,datetime.datetime.now())

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
        print("******* ERROR Fetching Orders Data ********", e)

    for ind in df.index:
        status = df['status'][ind]
        if status == "OPEN":
            token = df['tradingsymbol'][ind]
            orderslist[token] = 0
        #print(df['tradingsymbol'][ind], df['transaction_type'][ind]) 

    print(orderslist)
    return df

def run():
    global runcount
    global exitcount
    start_time = int(12) * 60 + int(1)  # specify in int (hr) and int (min) foramte
    end_time = int(14) * 60 + int(55)  # do not place fresh order
    square_time = int(15) * 60 + int(5)  # square off all open positions

    next_time = start_time

    if (datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5)))%10 == 0:
        next_time = datetime.datetime.now().hour * 60 + \
            ((datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5))) + 5)

    else :
        next_time = datetime.datetime.now().hour * 60 + \
            (datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5)))

    schedule_interval = 600  # run at every 1 min

    time_offset = (5 - (datetime.datetime.now().minute % 5)) * 60
    exit_time = datetime.datetime.now().hour * 60 + \
            (datetime.datetime.now().minute + (5 - (datetime.datetime.now().minute % 5)))
    #runcount = 0
    check_order_status()
    while True:
        check_order_status(immediate=True)
        #time.sleep(1)
        if (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= square_time:
            check_order_status(force=True)
            print("***** Trading day closed *****")
            break

        elif (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) >= start_time:

            if datetime.datetime.now().hour * 60 + datetime.datetime.now().minute >= exit_time:
                exit_time = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute + 5
                time.sleep(2)
                print("\n\n {} Exit Count : Time - {} ".format(exitcount, datetime.datetime.now()))
                if exitcount >= 0:
                    try:
                        check_order_status()
                    except Exception as e:
                        print("******* Run Error *********", e)
                exitcount = exitcount + 1

            if datetime.datetime.now().hour * 60 + datetime.datetime.now().minute >= next_time:
                next_time = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute + 10
                time.sleep(2)
                print("\n\n {} Run Count : Time - {} ".format(runcount, datetime.datetime.now()))
                if runcount >= 0:
                    try:
                        run_strategy()
                    except Exception as e:
                        print("******* Run Error *********", e)
                runcount = runcount + 1

        else:
            print('****** Waiting ********', datetime.datetime.now())
            time.sleep(5)


runcount = 0

run1()

