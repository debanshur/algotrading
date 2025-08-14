import datetime
import logging
import os
import sys

from kiteconnect import KiteConnect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import auth
from utils import historical_data

logging.basicConfig(level=logging.INFO)

# Get authentication data
userdata = auth.get_userdata()
kite = KiteConnect(api_key=userdata['api_key'])
kite.set_access_token(userdata['access_token'])

# Set parameters for historical data
token = 779521  # SBIN token
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=30)  # Last 30 days
interval = "day"  # Daily candles

# Fetch historical data
df = historical_data.get(kite, token, start_date, end_date, interval)
print("\nHistorical Data for SBIN:")
print(df.tail())  # Print last 5 entries
