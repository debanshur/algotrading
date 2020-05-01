import logging
from kiteconnect import KiteConnect
from modules import auth

logging.basicConfig(level=logging.INFO)

userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

# Place an order

try:
    order_id = kite.place_order(
        variety=kite.VARIETY_AMO,
        exchange=kite.EXCHANGE_NSE,
        tradingsymbol="SBIN",
        transaction_type=kite.TRANSACTION_TYPE_BUY,
        quantity=10,
        product=kite.PRODUCT_CNC,
        order_type=kite.ORDER_TYPE_MARKET
    )

    logging.info("Order placed. ID is: {}".format(order_id))
except Exception as e:
    logging.info("Order placement failed: {}".format(e.message))

# Fetch all orders
orders = kite.orders()
print(orders)

