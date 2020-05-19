
import datetime
from kiteconnect import KiteConnect
from modules import auth
from modules import historical_data
import pandas as pd

"""
1. Login to kite
"""
userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

print("******** UserData Loaded ********* : ", datetime.datetime.now())

val = 20

interval = "10minute"


#list all tickers you want to trade
#tickerlist = ["BAJAJFINSV"]
#tokenlist = [4268801]

tickerlist = ["BANKNIFTY20MAYFUT"]
tokenlist = [13430018]

#F&O nse 100
#tickerlist = ['BAJAJFINSV', 'BRITANNIA', 'ULTRACEMCO', 'BAJFINANCE', 'SRF', 'DRREDDY', 'BAJAJ-AUTO', 'NAUKRI', 'HINDUNILVR', 'ASIANPAINT', 'HDFC', 'HEROMOTOCO', 'TCS', 'NIITTECH', 'DIVISLAB', 'KOTAKBANK', 'PVR', 'TORNTPHARM', 'APOLLOHOSP', 'ACC', 'INDIGO', 'RELIANCE', 'JUBLFOOD', 'PIDILITIND', 'BATAINDIA', 'HDFCBANK', 'PEL', 'LT', 'SIEMENS', 'MGL', 'GODREJPROP', 'SRTRANSFIN', 'COLPAL', 'UBL', 'MUTHOOTFIN', 'TITAN', 'SBILIFE', 'MINDTREE', 'BALKRISIND', 'INDUSINDBK', 'LUPIN', 'RAMCOCEM', 'GRASIM', 'GODREJCP', 'AMARAJABAT', 'HAVELLS', 'VOLTAS', 'BERGEPAINT', 'ESCORTS', 'HDFCLIFE', 'INFY', 'TECHM', 'CUMMINSIND', 'AXISBANK', 'DABUR', 'MCDOWELL-N', 'CIPLA', 'MFSL', 'AUROPHARMA', 'UPL', 'ICICIBANK', 'IGL', 'CENTURYTEX', 'HCLTECH', 'SUNPHARMA', 'JUSTDIAL', 'M&M', 'TVSMOTOR', 'BHARATFORG', 'ICICIPRULI', 'SUNTV', 'CONCOR', 'TATASTEEL', 'BPCL', 'BANDHANBNK', 'BHARTIARTL', 'LICHSGFIN', 'MARICO', 'TATACHEM', 'M&MFIN', 'CADILAHC', 'UJJIVAN', 'BIOCON', 'GLENMARK', 'ADANIPORTS', 'CHOLAFIN', 'RBLBANK', 'HINDPETRO', 'JSWSTEEL', 'TATACONSUM', 'INFRATEL', 'AMBUJACEM', 'PETRONET', 'SBIN', 'TORNTPOWER', 'ZEEL', 'IBULHSGFIN', 'WIPRO', 'ITC', 'DLF']
#tokenlist = [4268801, 140033, 2952193, 81153, 837889, 225537, 4267265, 3520257, 356865, 60417, 340481, 345089, 2953217, 2955009, 2800641, 492033, 3365633, 900609, 40193, 5633, 2865921, 738561, 4632577, 681985, 94977, 341249, 617473, 2939649, 806401, 4488705, 4576001, 1102337, 3876097, 4278529, 6054401, 897537, 5582849, 3675137, 85761, 1346049, 2672641, 523009, 315393, 2585345, 25601, 2513665, 951809, 103425, 245249, 119553, 408065, 3465729, 486657, 1510401, 197633, 2674433, 177665, 548353, 70401, 2889473, 1270529, 2883073, 160001, 1850625, 857857, 7670273, 519937, 2170625, 108033, 4774913, 3431425, 1215745, 895745, 134657, 579329, 2714625, 511233, 1041153, 871681, 3400961, 2029825, 4369665, 2911489, 1895937, 3861249, 175361, 4708097, 359937, 3001089, 878593, 7458561, 325121, 2905857, 779521, 3529217, 975873, 7712001, 969473, 424961, 3771393]

#nifty50
#tickerlist = ['BAJAJ-AUTO', 'BAJFINANCE', 'HEROMOTOCO', 'HINDUNILVR', 'TCS', 'HDFC', 'ASIANPAINT', 'RELIANCE', 'KOTAKBANK', 'HDFCBANK', 'LT', 'TITAN', 'INFY', 'CIPLA', 'BHARTIARTL', 'TECHM', 'HCLTECH', 'GRASIM', 'SUNPHARMA', 'INDUSINDBK', 'AXISBANK', 'M&M', 'UPL', 'ICICIBANK', 'BPCL', 'ADANIPORTS', 'TATASTEEL', 'INFRATEL', 'WIPRO', 'JSWSTEEL', 'SBIN', 'ITC', 'POWERGRID', 'ZEEL', 'COALINDIA', 'HINDALCO']
#tokenlist = [4267265, 81153, 345089, 356865, 2953217, 340481, 60417, 738561, 492033, 341249, 2939649, 897537, 408065, 177665, 2714625, 3465729, 1850625, 315393, 857857, 1346049, 1510401, 519937, 2889473, 1270529, 134657, 3861249, 895745, 7458561, 969473, 3001089, 779521, 424961, 3834113, 975873, 5215745, 348929]



#Lets build a function for the strategy
def strategy(records, token):
    total_closing_price = 0
    record_count = 0
    order_placed = False
    last_order_placed = None
    last_order_price = 0
    profit = 0

    for record in records:
        record_count += 1
        #print(record)
        total_closing_price += record['close']

        #Moving average is calculated for every 5 ticks
        if record_count >= val:
            moving_average = total_closing_price/val
            #If moving average is greater than the last tick, we place a buy order
            if record['close'] > moving_average:
                if last_order_placed == "SELL" or last_order_placed is None:

                    #If last order was Sell, we need to exit the stock first
                    if last_order_placed == "SELL":
                        #print("Exit SELL")

                        #Calculate Profit
                        profit += last_order_price - record['close']
                        last_order_price = record['close']

                    #New Buy Order
                    #print("Place a new BUY Order")
                    last_order_placed = "BUY"

            #If moving average is less than the last tick and there is a position, place a sell order
            elif record['close'] < moving_average:
                if last_order_placed == "BUY":

                    #As last trade was a buy, lets exit it first
                    #print("Exit BUY")

					#Calculate Profit again
                    profit += record['close'] - last_order_price
                    last_order_price = record['close']

                    #Fresh SELL Order
                    #print("Place new SELL Order")
                    last_order_placed = "SELL"

            total_closing_price -= records[record_count - val]['close']
    print("Gross Profit",profit,"\n\n")
    #Place the last order
    #print(last_order_placed)
    #place_order(last_order_placed, token)


#Place an order based on the transaction type(BUY/SELL)
def place_order(transaction_type, token):
    print("**",transaction_type,token)
    kite.place_order(variety="regular",tradingsymbol = token, exchange = "NSE", quantity = 1, transaction_type=transaction_type,
                    order_type="MARKET",product="CNC")

def start():
    print("************ Backtesting Started *************")
    for i in range(0, len(tickerlist)):

        #startdate = enddate - datetime.timedelta(1)
        startdate = datetime.datetime(2020, 3, 15)
        enddate = datetime.datetime(2020, 4, 15)
        #enddate = datetime.datetime.today()

        print(interval)
        records = kite.historical_data(tokenlist[i], startdate, enddate, interval)

        #print("\n\n", records)

        #historical_data.get(kite, tokenlist[i], startdate, enddate, interval)
        print("\n************* ", tickerlist[i], "************")
        strategy(records, tokenlist[i])

start()


