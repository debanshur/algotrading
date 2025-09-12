import datetime
import os
import sys
import time

import pandas as pd
import pytz
from kiteconnect import KiteConnect

# Add root directory to Python path to access indicators module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from zerodha.utils import auth
from zerodha.utils import historical_data

from indicators import MACD, RSI, EMA, MFI, VWAP

# IST timezone setup
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current time in IST timezone"""
    return datetime.datetime.now(IST)

def get_ist_today():
    """Get today's date in IST timezone"""
    return datetime.datetime.now(IST)

max_amount_per_scrip = 3500
candlesize = '10minute'
orderslist = {}
mfilist = {}
trailing_sl = {}
pending_exit_orders = {}  # Track pending exit orders to prevent duplicates
one_hour_rsi = 50
one_hour_mfi = 50
reason = ""

run_count = 0
exitcount = 0

# pd.set_option('display.max_columns',50)
pd.set_option('display.max_rows', None)
print("\n******** Started ********* : ", get_ist_now())

"""
1. Login to kite
"""
userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

print("******** UserData Loaded ********* : ", get_ist_now())

# list all tickers you want to trade
tickerlist = ["RELIANCE"]
tokenlist = [738561]

# F&O nse 100
# tickerlist = ['BAJAJFINSV', 'BRITANNIA', 'ULTRACEMCO', 'BAJFINANCE', 'SRF', 'DRREDDY', 'BAJAJ-AUTO', 'NAUKRI', 'HINDUNILVR', 'ASIANPAINT', 'HDFC', 'HEROMOTOCO', 'TCS', 'NIITTECH', 'DIVISLAB', 'KOTAKBANK', 'PVR', 'TORNTPHARM', 'APOLLOHOSP', 'ACC', 'INDIGO', 'RELIANCE', 'JUBLFOOD', 'PIDILITIND', 'BATAINDIA', 'HDFCBANK', 'PEL', 'LT', 'SIEMENS', 'MGL', 'GODREJPROP', 'SRTRANSFIN', 'COLPAL', 'UBL', 'MUTHOOTFIN', 'TITAN', 'SBILIFE', 'MINDTREE', 'BALKRISIND', 'INDUSINDBK', 'LUPIN', 'RAMCOCEM', 'GRASIM', 'GODREJCP', 'AMARAJABAT', 'HAVELLS', 'VOLTAS', 'BERGEPAINT', 'ESCORTS', 'HDFCLIFE', 'INFY', 'TECHM', 'CUMMINSIND', 'AXISBANK', 'DABUR', 'MCDOWELL-N', 'CIPLA', 'MFSL', 'AUROPHARMA', 'UPL', 'ICICIBANK', 'IGL', 'CENTURYTEX', 'HCLTECH', 'SUNPHARMA', 'JUSTDIAL', 'M&M', 'TVSMOTOR', 'BHARATFORG', 'ICICIPRULI', 'SUNTV', 'CONCOR', 'TATASTEEL', 'BPCL', 'BANDHANBNK', 'BHARTIARTL', 'LICHSGFIN', 'MARICO', 'TATACHEM', 'M&MFIN', 'CADILAHC', 'UJJIVAN', 'BIOCON', 'GLENMARK', 'ADANIPORTS', 'CHOLAFIN', 'RBLBANK', 'HINDPETRO', 'JSWSTEEL', 'TATACONSUM', 'INFRATEL', 'AMBUJACEM', 'PETRONET', 'SBIN', 'TORNTPOWER', 'ZEEL', 'IBULHSGFIN', 'WIPRO', 'ITC', 'DLF']
# tokenlist = [4268801, 140033, 2952193, 81153, 837889, 225537, 4267265, 3520257, 356865, 60417, 340481, 345089, 2953217, 2955009, 2800641, 492033, 3365633, 900609, 40193, 5633, 2865921, 738561, 4632577, 681985, 94977, 341249, 617473, 2939649, 806401, 4488705, 4576001, 1102337, 3876097, 4278529, 6054401, 897537, 5582849, 3675137, 85761, 1346049, 2672641, 523009, 315393, 2585345, 25601, 2513665, 951809, 103425, 245249, 119553, 408065, 3465729, 486657, 1510401, 197633, 2674433, 177665, 548353, 70401, 2889473, 1270529, 2883073, 160001, 1850625, 857857, 7670273, 519937, 2170625, 108033, 4774913, 3431425, 1215745, 895745, 134657, 579329, 2714625, 511233, 1041153, 871681, 3400961, 2029825, 4369665, 2911489, 1895937, 3861249, 175361, 4708097, 359937, 3001089, 878593, 7458561, 325121, 2905857, 779521, 3529217, 975873, 7712001, 969473, 424961, 3771393]

# nifty50 - FULL
# tickerlist = ['WIPRO', 'INFY', 'HDFCLIFE', 'ETERNAL', 'HDFCBANK', 'EICHERMOT', 'ICICIBANK', 'BAJAJFINSV', 'BHARTIARTL', 'POWERGRID', 'SBIN', 'ADANIENT', 'TITAN', 'ASIANPAINT', 'HCLTECH', 'HINDUNILVR', 'MARUTI', 'DRREDDY', 'CIPLA', 'TRENT', 'GRASIM', 'AXISBANK', 'BAJFINANCE', 'APOLLOHOSP', 'TATAMOTORS', 'SUNPHARMA', 'RELIANCE', 'M&M', 'SBILIFE', 'TATACONSUM', 'BAJAJ-AUTO', 'INDUSINDBK', 'TCS', 'TECHM', 'KOTAKBANK', 'ITC', 'COALINDIA', 'NTPC', 'JSWSTEEL', 'NESTLEIND', 'ONGC', 'SHRIRAMFIN', 'HEROMOTOCO', 'LT', 'JIOFIN', 'BEL', 'HINDALCO', 'ULTRACEMCO', 'ADANIPORTS', 'TATASTEEL']
# tokenlist  = [969473, 408065, 119553, 1304833, 341249, 232961, 1270529, 4268801, 2714625, 3834113, 779521, 6401, 897537, 60417, 1850625, 356865, 2815745, 225537, 177665, 502785, 315393, 1510401, 81153, 40193, 884737, 857857, 738561, 519937, 5582849, 878593, 4267265, 1346049, 2953217, 3465729, 492033, 424961, 5215745, 2977281, 3001089, 4598529, 633601, 1102337, 345089, 2939649, 4644609, 98049, 348929, 2952193, 3861249, 895745]


# nifty50 < 3500
tickerlist = ['WIPRO', 'INFY', 'ETERNAL', 'HDFCLIFE', 'BAJAJFINSV', 'TITAN', 'ASIANPAINT', 'SBIN', 'HDFCBANK',
              'ICICIBANK', 'ADANIENT', 'BHARTIARTL', 'DRREDDY', 'AXISBANK', 'POWERGRID', 'SBILIFE', 'CIPLA', 'GRASIM',
              'M&M', 'SUNPHARMA', 'RELIANCE', 'TATAMOTORS', 'BAJFINANCE', 'HCLTECH', 'TCS', 'NTPC', 'KOTAKBANK',
              'INDUSINDBK', 'COALINDIA', 'ITC', 'HINDUNILVR', 'ONGC', 'TATACONSUM', 'JIOFIN', 'SHRIRAMFIN', 'BEL',
              'NESTLEIND', 'JSWSTEEL', 'TECHM', 'HINDALCO', 'ADANIPORTS', 'TATASTEEL']
tokenlist = [969473, 408065, 1304833, 119553, 4268801, 897537, 60417, 779521, 341249, 1270529, 6401, 2714625, 225537,
             1510401, 3834113, 5582849, 177665, 315393, 519937, 857857, 738561, 884737, 81153, 1850625, 2953217,
             2977281, 492033, 1346049, 5215745, 424961, 356865, 633601, 878593, 4644609, 1102337, 98049, 4598529,
             3001089, 3465729, 348929, 3861249, 895745]

blacklist = []


def compute_data(token):
    global one_hour_rsi
    global one_hour_mfi
    # enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    enddate = get_ist_today()
    startdate = enddate - datetime.timedelta(15)  # 12
    try:
        df = historical_data.get(kite, token, startdate, enddate, candlesize)
        df = EMA.calc(df, 'close', 'ema_5', 5)
        df = EMA.calc(df, 'close', 'ema_20', 20)
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
    # enddate = datetime.datetime(2020, 5, 4, 15,30,0,0)
    enddate = get_ist_today()
    startdate = enddate - datetime.timedelta(15)  # 12
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
    elif open > 400 and open <= 700 and volume >= 500000:
        return True
    elif open > 700 and open <= 1000 and volume >= 300000:
        return True
    elif open > 1000 and volume >= 100000:
        return True
    else:
        return False


def check_pending_exit_order(tradingsymbol):
    """
    Check if there's already a pending exit order for the given symbol.
    Returns True if pending order exists, False otherwise.
    """
    global pending_exit_orders
    
    if tradingsymbol not in pending_exit_orders:
        return False
    
    order_id = pending_exit_orders[tradingsymbol]
    
    try:
        # Check order status
        order_history = kite.order_history(order_id)
        if order_history:
            latest_status = order_history[-1]['status']
            # If order is completed, rejected, or cancelled, remove from pending
            if latest_status in ['COMPLETE', 'REJECTED', 'CANCELLED']:
                del pending_exit_orders[tradingsymbol]
                return False
            # If order is still pending/open, return True
            elif latest_status in ['OPEN', 'TRIGGER PENDING']:
                print(f"Pending exit order exists for {tradingsymbol}, order_id: {order_id}, status: {latest_status}")
                return True
        
        # If we can't get order history, assume order doesn't exist
        del pending_exit_orders[tradingsymbol]
        return False
        
    except Exception as e:
        print(f"Error checking order status for {tradingsymbol}: {e}")
        # On error, assume no pending order to avoid blocking legitimate exits
        if tradingsymbol in pending_exit_orders:
            del pending_exit_orders[tradingsymbol]
        return False


def robust_check_order_status(immediate=False, force=False, max_retries=3, retry_delay=5):
    """
    Robust order status checking with limited retries and proper error handling.
    Returns the result of check_order_status() or None if all retries failed.
    """
    for attempt in range(max_retries + 1):  # max_retries + 1 to include initial attempt
        try:
            status = check_order_status(immediate=immediate, force=force)
            if status is not None:
                return status
            
            if attempt < max_retries:
                print(f"***** Retry {attempt + 1}/{max_retries} Checking Order Status *****")
                time.sleep(retry_delay)
            else:
                print(f"***** All {max_retries} retries failed - giving up *****")
                
        except Exception as e:
            print(f"***** Error in order status check (attempt {attempt + 1}/{max_retries + 1}): {e} *****")
            if attempt < max_retries:
                print(f"***** Waiting {retry_delay} seconds before retry *****")
                time.sleep(retry_delay)
            else:
                print(f"***** All retries exhausted due to errors *****")
                break
    
    return None


def run_strategy():
    global orderslist
    global mfilist
    global trailing_sl
    global one_hour_rsi
    global one_hour_mfi
    for i in range(0, len(tickerlist)):

        if (tickerlist[i] in orderslist):
            continue
        if (tickerlist[i] in blacklist):
            continue
        try:
            histdata = compute_data(tokenlist[i])
            # print(histdata)
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

            # print("-----------------------------------------------------------------------------------------")
            print(tickerlist[i], open, close, "::::", round(ema5, 2), round(ema20, 2), round(macd, 4), int(mfi),
                  int(rsi), int(one_hour_mfi), int(one_hour_rsi), round(vwap, 2), round(perc_change, 2), volume)

            if (ema5 > ema20) and (pre_ema5 < pre_ema20) and (macd > 0) and (close > vwap) and \
                    (one_hour_mfi > 40) and (one_hour_mfi < 70) and (one_hour_rsi > 40) and (mfi < 70):
                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (max_amount_per_scrip / high)))
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

                print("         Order : ", "BUY", tickerlist[i], "quantity:", quantity, "macd", round(macd, 4), "mfi:",
                      round(mfi, 2), "rsi:", round(rsi, 2), \
                      "mfi_1hour:", round(one_hour_mfi, 2), "rsi_1hour:", round(one_hour_rsi, 2), "volume:", volume,
                      get_ist_now())

            if (ema5 < ema20) and (pre_ema5 > pre_ema20) and (macd < 0) and (close < vwap) and (one_hour_mfi > 30) and (
                    one_hour_mfi < 60) and (one_hour_rsi < 60):
                if not has_volume:
                    print("Sorry, Volume is low")
                    # continue

                if abs(perc_change) > 4:
                    print("Ignoring spike")
                    continue

                quantity = round(max(1, (max_amount_per_scrip / high)))
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

                print("         Order : ", "SELL", tickerlist[i], "quantity:", quantity, "macd", round(macd, 4), "mfi:",
                      round(mfi, 2), "rsi:", round(rsi, 2), \
                      "mfi_1hour:", round(one_hour_mfi, 2), "rsi_1hour:", round(one_hour_rsi, 2), "volume:", volume,
                      get_ist_now())

        except Exception as e:
            print(e)


def check_perc(tradingsymbol, average_price, last_price):
    global trailing_sl
    global reason
    exit_con = 0
    perc = (abs(average_price - last_price) * 100) / average_price
    if perc > 2.05:
        trailing_sl[tradingsymbol] = 2
    elif perc > 1.55:
        trailing_sl[tradingsymbol] = 1.5
    elif perc > 1.05:
        trailing_sl[tradingsymbol] = 1
    elif perc > 0.55:
        trailing_sl[tradingsymbol] = 0.5
    else:
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


def macd_condition_buy_exit(macd_value):
    """Check MACD condition for exiting buy positions (SELL orders)."""
    return macd_value < 0


def macd_condition_sell_exit(macd_value):
    """Check MACD condition for exiting sell positions (BUY orders)."""
    return macd_value > 0


def mfi_condition_buy_exit(mfi_stored, mfi_current):
    """Check MFI condition for exiting buy positions (SELL orders)."""
    return mfi_stored > 79 and mfi_current < 69


def mfi_condition_sell_exit(mfi_stored, mfi_current):
    """Check MFI condition for exiting sell positions (BUY orders)."""
    return mfi_stored < 21 and mfi_current > 31


def mfi_comparison_buy_exit(stored, current):
    """MFI comparison for buy positions - take higher MFI value."""
    return stored < current


def mfi_comparison_sell_exit(stored, current):
    """MFI comparison for sell positions - take lower MFI value."""
    return stored > current


def execute_exit_order(data, idx, immediate, force, transaction_type, macd_condition_func, mfi_condition_func, mfi_comparison_func):
    """
    Common function to execute exit orders for both buy and sell positions.
    
    Args:
        data: Position data (DataFrame slice)
        idx: Index of the position (for reference, but we'll use the actual index)
        immediate: Whether to execute immediately
        force: Whether to force exit
        transaction_type: "SELL" for exit_buy, "BUY" for exit_sell
        macd_condition_func: Function to check MACD condition (lambda hist_macd: condition)
        mfi_condition_func: Function to check MFI condition (lambda mfi_stored, mfi_current: condition)
        mfi_comparison_func: Function to compare MFI values (lambda stored, current: comparison)
    """
    global trailing_sl
    global reason
    global pending_exit_orders
    global orderslist
    global mfilist
    
    # Get the actual index from the DataFrame (since df.iloc[[idx]] creates new indexing)
    actual_idx = data.index[0]
    
    try:
        token = data['instrument_token'].iloc[0]
        average_price = data['average_price'].iloc[0]
        last_price = data['last_price'].iloc[0]
        tradingsymbol = data['tradingsymbol'].iloc[0]
        quantity = abs(data['quantity'].iloc[0])
        
        # Convert to appropriate types
        token = int(token) if not pd.isna(token) else 0
        average_price = float(average_price) if not pd.isna(average_price) else 0.0
        last_price = float(last_price) if not pd.isna(last_price) else 0.0
        quantity = int(quantity) if not pd.isna(quantity) else 0
        
    except Exception as e:
        print(f"******* ERROR extracting data for {tradingsymbol if 'tradingsymbol' in locals() else 'Unknown'}: {e}")
        return

    # Check if position still exists with non-zero quantity before placing exit order
    try:
        current_positions = kite.positions()['day']
        current_df = pd.DataFrame.from_dict(current_positions, orient='columns', dtype=None)
        
        position_exists = False
        if not current_df.empty and 'tradingsymbol' in current_df.columns and 'quantity' in current_df.columns:
            # Find the position for this tradingsymbol
            position_rows = current_df[current_df['tradingsymbol'] == tradingsymbol]
            if not position_rows.empty:
                current_quantity = position_rows['quantity'].iloc[0]
                if pd.notna(current_quantity) and float(current_quantity) != 0:
                    position_exists = True
        
        if not position_exists:
            print(f"Position no longer exists or quantity is zero for {tradingsymbol} - skipping exit order")
            # Clean up tracking dictionaries for closed positions
            if tradingsymbol in orderslist:
                del orderslist[tradingsymbol]
            if tradingsymbol in mfilist:
                del mfilist[tradingsymbol]
            if tradingsymbol in trailing_sl:
                del trailing_sl[tradingsymbol]
            if tradingsymbol in pending_exit_orders:
                del pending_exit_orders[tradingsymbol]
            return
            
    except Exception as e:
        print(f"******* ERROR checking current positions for {tradingsymbol}: {e}")
        # Continue with exit order if we can't verify position status
        print(f"Continuing with exit order placement due to position check error")

    if force:
        reason = "Time up"

    if average_price <= 0:
        return

    # Check if there's already a pending exit order for this symbol
    if check_pending_exit_order(tradingsymbol):
        print(f"Skipping exit for {tradingsymbol} - pending exit order already exists")
        return

    exit_con = 0

    if immediate:
        exit_con = check_perc(tradingsymbol, average_price, last_price)

    else:
        histdata = exit_data(token)
        if tradingsymbol not in mfilist:
            mfilist[tradingsymbol] = histdata.mfi.values[-2]
        else:
            # Use the comparison function to determine whether to update MFI
            if mfi_comparison_func(mfilist[tradingsymbol], histdata.mfi.values[-2]):
                mfilist[tradingsymbol] = histdata.mfi.values[-2]

        # Initialize trailing_sl if not exists
        if tradingsymbol not in trailing_sl:
            trailing_sl[tradingsymbol] = 0
            
        print(tradingsymbol, last_price, histdata.hist_12_26_9.values[-2], mfilist[tradingsymbol],
              histdata.mfi.values[-2], trailing_sl[tradingsymbol])

        exit_con = check_perc(tradingsymbol, average_price, last_price)

        # Check MACD condition
        if macd_condition_func(histdata.hist_12_26_9.values[-2]):
            exit_con = 1
            reason = "macd change"
        # Check MFI condition
        elif mfi_condition_func(mfilist[tradingsymbol], histdata.mfi.values[-2]):
            exit_con = 1
            reason = "mfi change" if transaction_type == "SELL" else "mfi condition"

    if exit_con == 1 or force:
        try:
            order = kite.place_order(exchange='NSE',
                                     tradingsymbol=tradingsymbol,
                                     transaction_type=transaction_type,
                                     quantity=quantity,
                                     product='MIS',
                                     order_type='MARKET',
                                     validity='DAY',
                                     variety="regular"
                                     )

            # Track the order ID to prevent duplicates
            if order and 'order_id' in order:
                pending_exit_orders[tradingsymbol] = order['order_id']
                print(f"         Exit order placed: {transaction_type} {tradingsymbol}, order_id: {order['order_id']}, price: {last_price}, reason: {reason}, time: {get_ist_now()}")
            else:
                print(f"         Exit order placed: {transaction_type} {tradingsymbol}, price: {last_price}, reason: {reason}, time: {get_ist_now()}")

            # Clean up tracking dictionaries after successful order placement
            if tradingsymbol in orderslist:
                del orderslist[tradingsymbol]
            if tradingsymbol in mfilist:
                del mfilist[tradingsymbol]
            if tradingsymbol in trailing_sl:
                del trailing_sl[tradingsymbol]

        except Exception as e:
            print(f"Error placing exit order for {tradingsymbol}: {e}")
            # Don't clean up dictionaries if order placement failed
            # This allows for retry in the next iteration
            raise e  # Re-raise the exception to be handled by check_order_status


def exit_buy(data, idx, immediate, force):
    """Exit a buy position by placing a sell order."""
    execute_exit_order(
        data=data,
        idx=idx,
        immediate=immediate,
        force=force,
        transaction_type="SELL",
        macd_condition_func=macd_condition_buy_exit,
        mfi_condition_func=mfi_condition_buy_exit,
        mfi_comparison_func=mfi_comparison_buy_exit
    )


def exit_sell(data, idx, immediate, force):
    """Exit a sell position by placing a buy order."""
    execute_exit_order(
        data=data,
        idx=idx,
        immediate=immediate,
        force=force,
        transaction_type="BUY",
        macd_condition_func=macd_condition_sell_exit,
        mfi_condition_func=mfi_condition_sell_exit,
        mfi_comparison_func=mfi_comparison_sell_exit
    )


def calculate_next_times(current_time=None):
    if current_time is None:
        current_time = get_ist_now()
    
    current_minutes = current_time.hour * 60 + current_time.minute
    
    # Calculate next strategy execution time (10-minute intervals)
    # Align with candle boundaries: 9:15, 9:25, 9:35, etc.
    if (current_time.minute + (5 - (current_time.minute % 5))) % 10 == 0:
        strategy_time = current_time.hour * 60 + \
                       ((current_time.minute + (5 - (current_time.minute % 5))) + 5)
    else:
        strategy_time = current_time.hour * 60 + \
                       (current_time.minute + (5 - (current_time.minute % 5)))
    
    # Calculate next exit check time (5-minute intervals)
    exit_time = current_time.hour * 60 + \
               (current_time.minute + (5 - (current_time.minute % 5)))
    
    return {
        'strategy_time': strategy_time,
        'exit_time': exit_time
    }


def update_next_strategy_time(current_minutes, start_time):
    """
    Update next strategy execution time to next 10-minute boundary from start_time.
    Strategy runs every 10 minutes starting from start_time.
    """
    if current_minutes < start_time:
        return start_time
    
    # Calculate how many intervals have passed since start_time
    intervals_passed = (current_minutes - start_time) // 10
    return start_time + (intervals_passed + 1) * 10


def update_next_exit_time(current_minutes, start_time):
    """
    Update next exit check time to next 5-minute boundary from start_time.
    Exit checks run every 5 minutes starting from start_time.
    """
    if current_minutes < start_time:
        return start_time
    
    # Calculate how many intervals have passed since start_time
    intervals_passed = (current_minutes - start_time) // 5
    return start_time + (intervals_passed + 1) * 5


def check_order_status(immediate=False, force=False):
    print("***** Checking Order Status : immediate : {}, force : {}".format(immediate, force))
    global orderslist
    global mfilist
    global trailing_sl
    global pending_exit_orders
    # print(kite.positions()['day'])
    # orderslist.clear()

    df = pd.DataFrame(columns=['tradingsymbol', 'instrument_token', 'quantity', 'average_price', 'last_price', 'pnl'])
    try:
        data = kite.positions()['day']
        #print(data)
        df = pd.DataFrame.from_dict(data, orient='columns', dtype=None)

        if not df.empty:
            # Check if required columns exist
            required_columns = ['tradingsymbol', 'instrument_token', 'quantity', 'average_price', 'last_price', 'pnl']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"ERROR: Missing columns in positions data: {missing_columns}")
                print(f"Available columns: {df.columns.tolist()}")
                return None
            
            df = df[required_columns]
            print(df)
            for idx in df.index:
                try:
                    # Safely get values from DataFrame
                    tradingsymbol = df.loc[idx, 'tradingsymbol']
                    quantity = df.loc[idx, 'quantity']
                    average_price = df.loc[idx, 'average_price']
                    
                    # Convert to appropriate types if needed
                    if pd.isna(tradingsymbol) or tradingsymbol == '':
                        continue
                    
                    # Handle NaN values for numeric columns
                    if pd.isna(quantity):
                        quantity = 0
                    else:
                        quantity = float(quantity)
                    
                    if pd.isna(average_price):
                        average_price = 0
                    else:
                        average_price = float(average_price)
                    
                    if tradingsymbol in blacklist:
                        print("Not applicable <> Blacklist:", tradingsymbol)
                        continue

                    if tradingsymbol not in tickerlist:
                        print("Not applicable <> Missing in Tickerlist:", tradingsymbol)
                        continue

                    if quantity == 0:
                        # Clean up tracking dictionaries for closed positions
                        if tradingsymbol in orderslist:
                            del orderslist[tradingsymbol]
                        if tradingsymbol in mfilist:
                            del mfilist[tradingsymbol]
                        if tradingsymbol in trailing_sl:
                            del trailing_sl[tradingsymbol]
                        if tradingsymbol in pending_exit_orders:
                            del pending_exit_orders[tradingsymbol]

                    elif quantity > 0:
                        if tradingsymbol not in orderslist:
                            print("orderlist not present : " + tradingsymbol)
                            orderslist[tradingsymbol] = average_price

                        try:
                            exit_buy(df.iloc[[idx]], idx, immediate, force)
                        except Exception as exit_error:
                            print(f"******* ERROR in exit_buy for {tradingsymbol}: {exit_error}")
                        
                    elif quantity < 0:
                        if tradingsymbol not in orderslist:
                            print("orderlist not present : " + tradingsymbol)
                            orderslist[tradingsymbol] = average_price

                        try:
                            exit_sell(df.iloc[[idx]], idx, immediate, force)
                        except Exception as exit_error:
                            print(f"******* ERROR in exit_sell for {tradingsymbol}: {exit_error}")
                        
                except Exception as row_error:
                    print(f"******* ERROR processing row for {tradingsymbol if 'tradingsymbol' in locals() else 'Unknown'}: {row_error}")
                    print(f"Error details: {type(row_error).__name__}: {str(row_error)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    continue
                    
    except Exception as e:
        print("******* ERROR Check order ********", e)
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

    # print(df.iloc[[3]])

    # print(orderslist)
    if not immediate:
        print("orderslist:", orderslist)
        print("mfilist:", mfilist)
        print("trailing_sl:", trailing_sl)
        print("pending_exit_orders:", pending_exit_orders)
    
    # Calculate and display total PnL
    if not df.empty and 'pnl' in df.columns:
        # Filter out positions not in ticker list
        filtered_df = df[df['tradingsymbol'].isin(tickerlist)]
        total_pnl = filtered_df['pnl'].sum()
        
        print(f"Total PnL: {round(total_pnl)}")
    else:
        print("Total PnL: 0 (no positions)")
    
    return df


def run():
    global run_count
    global exitcount
    start_time = int(10) * 60 + int(55)  # specify in int (hr) and int (min) format
    end_time = int(14) * 60 + int(30)  # do not place fresh order
    square_time = int(15) * 60 + int(10)  # square off all open positions

    # Calculate initial execution times using consolidated function
    initial_times = calculate_next_times()
    next_time = initial_times['strategy_time']
    exit_time = initial_times['exit_time']
    
    # Ensure we don't start before the designated start_time
    if next_time < start_time:
        next_time = start_time

    schedule_interval = 600  # run at every 1 min
    # runcount = 0
    print("***** Checking Order Status : Before Loop *****")
    check_order_status()
    while True:
        now = get_ist_now()
        current_minutes = now.hour * 60 + now.minute

        # Immediate check with minimal retries to avoid timing disruption
        # This was the root cause of timing delays when connection errors occurred
        try:
            robust_check_order_status(immediate=True, max_retries=1, retry_delay=1)
        except Exception as e:
            print(f"******* ERROR in immediate check (continuing): {e}")
            # Continue the loop even if immediate check fails to preserve timing
        if (get_ist_now().hour * 60 + get_ist_now().minute) >= square_time:
            print("***** Squaring off Positions *****")
            status = robust_check_order_status(force=True, max_retries=10, retry_delay=3)
            if status is None:
                print("***** Warning: Could not verify square-off completion after retries *****")
            print("***** Trading day closed *****")
            break

        elif (get_ist_now().hour * 60 + get_ist_now().minute) >= start_time:
            # Refresh current time after potential delays from immediate check
            current_minutes = get_ist_now().hour * 60 + get_ist_now().minute

            # --- Exit check every 5 minutes (continues until square_time) ---
            if current_minutes >= exit_time:
                # Update to next 5-min boundary using consolidated function
                exit_time = update_next_exit_time(current_minutes, start_time)
                time.sleep(2)
                print("\n\n {} Exit Count : Time - {} ".format(exitcount, get_ist_now()))
                if exitcount >= 0:
                    try:
                        print("***** Checking Order Status : exitcount *****")
                        status = robust_check_order_status(max_retries=10, retry_delay=3)
                        if status is None:
                            print("***** Warning: Could not check order status after retries *****")
                    except Exception as e:
                        print("******* Run Error *********", e)
                exitcount = exitcount + 1

            # --- Strategy execution (only during trading window) ---
            if next_time <= current_minutes <= end_time:
                # Update to next 10-min boundary using consolidated function
                next_time = update_next_strategy_time(current_minutes, start_time)
                time.sleep(2)
                print("\n\n {} Run Count : Time - {} ".format(run_count, get_ist_now()))
                if run_count >= 0:
                    try:
                        run_strategy()
                    except Exception as e:
                        print("******* Run Error *********", e)
                run_count = run_count + 1

            # --- Status display and sleep logic ---
            current_time_minutes = get_ist_now().hour * 60 + get_ist_now().minute
            if current_time_minutes >= end_time:
                print('******  New Trade window closed ********', get_ist_now())
                print(f'******  Exit checks continue every 5 minutes until square-off ********')
                square_off_remaining = square_time - current_time_minutes
                print(f'******  Minutes until square-off (15:05) ******** {square_off_remaining} minutes')
            elif current_minutes < next_time:
                print('******  Waiting for next strategy time ********', get_ist_now())
                time_remaining_minutes = next_time - current_time_minutes
                print('******  Time Remaining ********', time_remaining_minutes, 'minutes')
            
            print('--------------------------------------------------------------------------------------')

            # --- Sleep logic ---
            now = get_ist_now()
            # Compute seconds until next minute's :05
            sleep_seconds = (60 - now.second) + 5
            if now.second < 5:
                # Already before :05 → just wait until this minute's :05
                sleep_seconds = 5 - now.second

            time.sleep(sleep_seconds)

        else:
            start_time = int(10) * 60 + int(55)
            print('****** Waiting for start time ********', get_ist_now())
            # time.sleep(5)
            now = get_ist_now()
            current_minutes = now.hour * 60 + now.minute

            # Calculate how many seconds to wait
            wait_minutes = start_time - current_minutes
            wait_seconds = wait_minutes * 60 - now.second  # subtract current seconds offset

            if wait_seconds > 0:
                print(f"****** Waiting for start time ******** {now} (sleeping {wait_seconds} seconds)")
                time.sleep(wait_seconds)


if __name__ == '__main__':
    print("Starting..")
    run()
