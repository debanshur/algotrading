import requests
from fyers_api import accessToken, fyersModel

from auth.json_util import get_json_value
access_token = get_json_value('access_token')
client_id = "TC8P3VH4H7-100"

fyers = fyersModel.FyersModel(token=access_token, is_async=False, client_id=client_id, log_path="/Users/debanshu.rout/repo/external/algotrading/log")

### After this point you can call the relevant apis and get started with

####################################################################################################################
"""
1. User Apis : This includes (Profile,Funds,Holdings)
"""
print("---- GET PROFILE----")
print(fyers.get_profile())  ## This will provide us with the user related data

print("---- GET FUNDS----")
print(fyers.funds())  ## This will provide us with the funds the user has

print("---- GET HOLDINGS----")
print(fyers.holdings())  ## This will provide the available holdings the user has

########################################################################################################################

"""
2. Transaction Apis : This includes (Tradebook,Orderbook,Positions)
"""

print("---- GET TRADEBOOK----")
print(fyers.tradebook())  ## This will provide all the trade related information

print("---- GET ORDERBOOK----")
print(fyers.orderbook())  ## This will provide the user with all the order realted information

print("---- GET POSITIONS----")
print(fyers.positions())  ## This will provide the user with all the positions the user has on his end

######################################################################################################################

"""
3. Order Placement  : This Apis helps to place order. 
There are two ways to place order 
a. single order : wherein you can fire one order at a time 
b. multi order : this is used to place a basket of order but the basket size can max be 10 symbols
"""

## SINGLE ORDER

data = {
    "symbol": "NSE:SBIN-EQ",
    "qty": 1,
    "type": 2,
    "side": 1,
    "productType": "INTRADAY",
    "limitPrice": 0,
    "stopPrice": 0,
    "validity": "DAY",
    "disclosedQty": 0,
    "offlineOrder": "False",
    "stopLoss": 0,
    "takeProfit": 0
}  ## This is a samplea example to place a limit order you can make the further changes based on your requriements

print("---- GET PLACE ORDER----")
print(fyers.place_order(data))

## MULTI ORDER

data = [{"symbol": "NSE:SBIN-EQ",
         "qty": 1,
         "type": 1,
         "side": 1,
         "productType": "INTRADAY",
         "limitPrice": 61050,
         "stopPrice": 0,
         "disclosedQty": 0,
         "validity": "DAY",
         "offlineOrder": "False",
         "stopLoss": 0,
         "takeProfit": 0
         },
        {
            "symbol": "NSE:HDFC-EQ",
            "qty": 1,
            "type": 2,
            "side": 1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "disclosedQty": 0,
            "validity": "DAY",
            "offlineOrder": "False",
            "stopLoss": 0,
            "takeProfit": 0
        }]  ### This takes input as a list containing multiple single order data into it and the execution of the orders goes in the same format as mentioned.

#print(fyers.place_basket_orders(data))

###################################################################################################################

"""
4. Other Transaction : This includes (modify_order,exit_position,cancel_order,convert_positions)
"""

## Modify_order request
data = {
    "id": 7574657627567,
    "type": 1,
    "limitPrice": 61049,
    "qty": 1
}

print("---- GET MODIFY ORDER----")
print(fyers.modify_order(data))

## Modify Multi Order

data = [
    {"id": 8102710298291,
     "type": 1,
     "limitPrice": 61049,
     "qty": 0
     },
    {
        "id": 8102710298292,
        "type": 1,
        "limitPrice": 61049,
        "qty": 1
    }]

#print(fyers.modify_basket_orders(data))

### Cancel_order
data = {"id": '808058117761'}

print("---- GET CANCEL ORDER----")
print(fyers.cancel_order(data))

### cancel_multi_order
data = [
    {
        "id": '808058117761'
    },
    {
        "id": '808058117762'
    }]

#print(fyers.cancel_basket_orders(data))

### Exit Position
data = {
    "id": "NSE:SBIN-EQ-INTRADAY"
}

print("---- GET EXIT ORDER----")
print(fyers.exit_positions(data))

### Convert Position

data = {
    "symbol": "MCX:SILVERMIC20NOVFUT",
    "positionSide": 1,
    "convertQty": 1,
    "convertFrom": "INTRADAY",
    "convertTo": "CNC"
}

#print(fyers.convert_position(data))

#################################################################################################################

"""
DATA APIS : This includes following Apis(History,Quotes,MarketDepth)
"""

## Historical Data

data = {"symbol": "NSE:SBIN-EQ", "resolution": "D", "date_format": "0", "range_from": "1622097600",
        "range_to": "1622097685", "cont_flag": "1"}

print("---- GET HISTORY DATA----")
print(fyers.history(data))

## Quotes

data = {"symbols": "NSE:SBIN-EQ"}
print("---- GET QUOTES DATA----")
print(fyers.quotes(data))

## Market Depth

data = {"symbol": "NSE:SBIN-EQ", "ohlcv_flag": "1"}
print("---- GET MARKET DEPTH DATA----")
print(fyers.depth(data))
