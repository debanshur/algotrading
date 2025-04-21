from kiteconnect import KiteConnect
import datetime
import pandas as pd
import time

from modules import auth
from modules import historical_data
from indicators import MACD, RSI, EMA, MFI, VWAP

candlesize = '10minute'
orderslist = {}
mfilist = {}
trailing_sl = {}
one_hour_rsi = 50
one_hour_mfi = 50
reason = ""

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
    global one_hour_mfi
    #enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(15) #12
    try:
        df = historical_data.get(kite, token, startdate, enddate, candlesize)
        df = EMA.calc(df,'close','ema_5',5)
        df = EMA.calc(df,'close','ema_20',20)
        df = MACD.calc(df)
        df = VWAP.calc(df)
        df = RSI.calc(df)
        df = MFI.calc(df)

        hour_data = historical_data.get(kite, token, startdate, enddate, "60minute")
        hour_data = RSI.calc(hour_data)
        hour_data = MFI.calc(hour_data)
        one_hour_rsi = hour_data.RSI_14.values[-2]
        one_hour_mfi = hour_data.mfi.values[-2]
        hour_data.drop(['RSI_14', 'mfi'], inplace=True, axis=1)

    except Exception as e:
        print("******* ERROR Computing Historical Data ********", token, e)
    return df


def exit_data(token):
    #enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(15) #12
    try:
        df = historical_data.get(kite, token, startdate, enddate, candlesize)
        df = MACD.calc(df)
        df = MFI.calc(df)

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
    global mfilist
    global trailing_sl
    global one_hour_rsi
    global one_hour_mfi
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
			rsi = histdata.RSI_14.values[-2]

            open = histdata.open.values[-2]
            close = histdata.close.values[-2]
            high = histdata.high.values[-2]
            low = histdata.low.values[-2]

            volume = histdata.volume.values[-2]
            has_volume = check_volume(histdata.open.values[-2], volume)

            perc_change = ((close - pre_close) * 100) / open

            #print("-----------------------------------------------------------------------------------------")
            print(tickerlist[i],open,close,"::::",round(ema5,2),round(ema20,2),round(macd,4),int(mfi),int(rsi),\
                int(one_hour_mfi),int(one_hour_rsi),round(vwap,2),round(perc_change,2),volume)

            if (ema5 > ema20) and (pre_ema5 < pre_ema20) and (macd > 0) and (close > vwap) and \
                            (one_hour_mfi > 40) and (one_hour_mfi < 70) and (one_hour_rsi > 40) and (mfi < 70):
                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (2500/high)))
                quantity = int(quantity)

                orderslist[tickerlist[i]] = close
                mfilist[tickerlist[i]] = mfi
                trailing_sl[tickerlist[i]] = 0

                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="BUY",
                                             quantity=quantity,
                                             product='MIS',
                                             order_type='MARKET',
                                             validity='DAY',
                                             variety="regular"
                                             )

                print("         Order : ","BUY",tickerlist[i],"quantity:",quantity,"macd",round(macd,4),"mfi:",round(mfi,2),"rsi:",round(rsi,2),\
                    "mfi_1hour:",round(one_hour_mfi,2),"rsi_1hour:",round(one_hour_rsi,2),"volume:",volume,datetime.datetime.now())

            if (ema5 < ema20) and (pre_ema5 > pre_ema20) and (macd < 0) and (close < vwap) and (one_hour_mfi > 30) and (one_hour_mfi < 60) and (one_hour_rsi < 60):
                if not has_volume:
                    print("Sorry, Volume is low")
                    #continue

                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (2500/high)))
                quantity = int(quantity)

                orderslist[tickerlist[i]] = close
                mfilist[tickerlist[i]] = mfi
                trailing_sl[tickerlist[i]] = 0

                order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tickerlist[i],
                                             transaction_type="SELL",
                                             quantity=quantity,
                                             product='MIS',
                                             order_type='MARKET',
                                             validity='DAY',
                                             variety="regular"
                                             )

                print("         Order : ","SELL",tickerlist[i],"quantity:",quantity,"macd",round(macd,4),"mfi:",round(mfi,2),"rsi:",round(rsi,2),\
                    "mfi_1hour:",round(one_hour_mfi,2),"rsi_1hour:",round(one_hour_rsi,2),"volume:",volume,datetime.datetime.now())

        except Exception as e :
            print(e)


def check_perc(tradingsymbol, average_price, last_price):
    global trailing_sl
    global reason
    exit_con = 0
    perc = (abs(average_price - last_price )*100) / average_price
    if perc > 2.05:
        trailing_sl[tradingsymbol] = 2
    elif perc > 1.55:
        trailing_sl[tradingsymbol] = 1.5
    elif perc > 1.05:
        trailing_sl[tradingsymbol] = 1
    elif perc > 0.55:
        trailing_sl[tradingsymbol] = 0.5
    else :
        trailing_sl[tradingsymbol] = 0

    if trailing_sl[tradingsymbol] == 2:
        if perc < 1.95:
            exit_con = 1
            reason = "immediate. Percentage Exit 2%"

    if trailing_sl[tradingsymbol] == 1.5:
        if perc < 1.45:
            exit_con = 1
            reason = "immediate. Percentage Exit 1.5%"

    if trailing_sl[tradingsymbol] == 1:
        if perc < 0.95:
            exit_con = 1
            reason = "immediate. Percentage Exit 1%"

    if trailing_sl[tradingsymbol] == 0.5:
        if perc < 0.5:
            exit_con = 1
            reason = "immediate. Percentage Exit 0.5%"
    return exit_con
	

def exit_buy(data, idx, immediate, force):
    #tradingsymbol  instrument_token  quantity  average_price  last_price
    #print(data)
    global trailing_sl
    global reason
    token = data['instrument_token'][idx]
    average_price = data['average_price'][idx]
    last_price = data['last_price'][idx]
    tradingsymbol = data['tradingsymbol'][idx]
    quantity = data['quantity'][idx]

    if force:
        reason = "Time up"

    if average_price <=0:
        return


    exit_con = 0

    if immediate:
        exit_con = check_perc(tradingsymbol, average_price, last_price)

    else :
        histdata = exit_data(token)
        if tradingsymbol not in mfilist:
            mfilist[tradingsymbol] = histdata.mfi.values[-2]

        else:
            if mfilist[tradingsymbol] < histdata.mfi.values[-2]:
                mfilist[tradingsymbol] = histdata.mfi.values[-2]

        print(tradingsymbol,last_price,histdata.hist_12_26_9.values[-2],mfilist[tradingsymbol],histdata.mfi.values[-2],trailing_sl[tradingsymbol])

        exit_con = check_perc(tradingsymbol, average_price, last_price)

        if histdata.hist_12_26_9.values[-2] < 0:
            exit_con = 1
            reason = "macd change"

        elif mfilist[tradingsymbol] > 79:
            if histdata.mfi.values[-2] < 69:
                exit_con = 1
                reason = "mfi change"

    if exit_con == 1 or force:
        order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tradingsymbol,
                                             transaction_type="SELL",
                                             quantity=quantity,
                                             product='MIS',
                                             order_type='MARKET',
                                             validity='DAY',
                                             variety="regular"
                                             )

        print("         Exit : ","SELL",tradingsymbol,"price:",last_price,reason,datetime.datetime.now())
        if tradingsymbol in orderslist:
            del orderslist[tradingsymbol]
        if tradingsymbol in mfilist:
            del mfilist[tradingsymbol]
        if tradingsymbol in trailing_sl:
            del trailing_sl[tradingsymbol]


def exit_sell(data,idx, immediate, force):
    #tradingsymbol  instrument_token  quantity  average_price  last_price
    #print(data)
    global trailing_sl
    global reason
    token = data['instrument_token'][idx]
    average_price = data['average_price'][idx]
    last_price = data['last_price'][idx]
    tradingsymbol = data['tradingsymbol'][idx]
    quantity = abs(data['quantity'][idx])

    if force:
        reason = "Time up"

    if average_price <=0:
        return


    exit_con = 0


    if immediate:
        exit_con = check_perc(tradingsymbol, average_price, last_price)

    else :
        histdata = exit_data(token)
        if tradingsymbol not in mfilist:
            mfilist[tradingsymbol] = histdata.mfi.values[-2]

        else:
            if mfilist[tradingsymbol] > histdata.mfi.values[-2]:
                mfilist[tradingsymbol] = histdata.mfi.values[-2]

        print(tradingsymbol,last_price,histdata.hist_12_26_9.values[-2],mfilist[tradingsymbol],histdata.mfi.values[-2],trailing_sl[tradingsymbol])

        exit_con = check_perc(tradingsymbol,average_price, last_price)

        if histdata.hist_12_26_9.values[-2] > 0:
            exit_con = 1
            reason = "macd change"

        elif mfilist[tradingsymbol] < 21:
            if histdata.mfi.values[-2] > 31:
                exit_con = 1
                reason = "mfi condition"

    if exit_con == 1 or force:
        order = kite.place_order(exchange='NSE',
                                             tradingsymbol=tradingsymbol,
                                             transaction_type="BUY",
                                             quantity=quantity,
                                             product='MIS',
                                             order_type='MARKET',
                                             validity='DAY',
                                             variety="regular"
                                             )

        print("         Exit : ","BUY",tradingsymbol,"price:",last_price,reason,datetime.datetime.now())
        if tradingsymbol in orderslist:
            del orderslist[tradingsymbol]
        if tradingsymbol in mfilist:
            del mfilist[tradingsymbol]
        if tradingsymbol in trailing_sl:
            del trailing_sl[tradingsymbol]
		

		
def check_order_status(immediate=False, force=False):
    global orderslist
    global mfilist
    global trailing_sl
    #print(kite.positions()['day'])
    #orderslist.clear()

    df = pd.DataFrame(columns=['tradingsymbol', 'instrument_token', 'quantity', 'average_price', 'last_price'])
    try:
        data = kite.positions()['day']
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)
        if not df.empty:
            df = df[['tradingsymbol', 'instrument_token', 'quantity', 'average_price', 'last_price']]
            for idx in df.index:
                if not df['tradingsymbol'][idx] in tickerlist:
                    #print("Not applicable :", df['tradingsymbol'][idx])
                    continue

                if df['quantity'][idx] == 0:
                    #df.drop([idx], inplace = True)
                    if df['tradingsymbol'][idx] in orderslist:
                        del orderslist[df['tradingsymbol'][idx]]

                    if df['tradingsymbol'][idx] in mfilist:
                        del mfilist[df['tradingsymbol'][idx]]

                    if df['tradingsymbol'][idx] in trailing_sl:
                        del trailing_sl[df['tradingsymbol'][idx]]

                elif df['quantity'][idx] > 0:
                    if not df['tradingsymbol'][idx] in orderslist:
                        print("orderlist empty. Suspicious")
                        orderslist[df['tradingsymbol'][idx]] = df['average_price'][idx]

                    exit_buy(df.iloc[[idx]], idx,immediate,force)
                elif df['quantity'][idx] < 0:
                    if not df['tradingsymbol'][idx] in orderslist:
                        print("orderlist empty. Suspicious")
                        orderslist[df['tradingsymbol'][idx]] = df['average_price'][idx]

                    exit_sell(df.iloc[[idx]],idx,immediate,force)
                #print(df['tradingsymbol'][idx], df['transaction_type'][idx])
    except Exception as e:
        print("******* ERROR Check order ********", e)

    #print(df.iloc[[3]])


    #print(orderslist)
    if not immediate:
        print(df)
        print(orderslist)
        print(mfilist)
        print(trailing_sl)
    return df


def run():
    global run_count
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


run_count = 0

#run1()
run()

