from kiteconnect import KiteConnect
import pandas as pd
import os
import sys
import datetime
import logging

logging.basicConfig(level=logging.INFO)

cur_dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
data_path = os.path.join(cur_dir_path, 'data')
userdata_file = os.path.join(data_path, 'userdata.csv')

def is_valid_token(api_key, access_token):
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        kite.profile()
        return True
    except Exception:
        return False

def get_userdata():
    try:
        if (os.path.exists(userdata_file)):
            userdata = pd.read_csv(userdata_file)
            api_key = userdata.loc[0, 'api_key']
            access_token = userdata.loc[0, 'access_token']
            user_id = userdata.loc[0, 'user_id']
            public_token = userdata.loc[0, 'public_token']
            if is_valid_token(api_key, access_token):
                data = ({"api_key": api_key, "access_token": access_token, \
                    "user_id": user_id, "public_token": public_token}) 
                return data

        raise Exception("** Run setup.py")
    except Exception as e:
        print("** ERROR in setup. ", e, datetime.datetime.now())