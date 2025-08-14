import logging
import os
import sys

from kiteconnect import KiteConnect

# Add parent directory to Python path to access utils module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import auth

logging.basicConfig(level=logging.INFO)

userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

# Place an order

try:
    order_id = kite.place_order(
        variety=kite.VARIETY_AMO,
        # variety=kite.VARIETY_REGULAR,
        exchange=kite.EXCHANGE_NSE,
        tradingsymbol="SBIN",
        transaction_type=kite.TRANSACTION_TYPE_BUY,
        quantity=1,
        product=kite.PRODUCT_CNC,
        order_type=kite.ORDER_TYPE_MARKET
    )

    logging.info("Order placed. ID is: {}".format(order_id))
except Exception as e:
    logging.info("Order placement failed: {}".format(e.message))

# Fetch all orders
if __name__ == '__main__':
    orders = kite.orders()
    print(orders)
