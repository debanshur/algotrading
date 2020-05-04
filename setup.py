from kiteconnect import KiteConnect
import pandas as pd
import os
import sys
import datetime
import logging
import math 

logging.basicConfig(level=logging.INFO)

cur_dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
data_path = os.path.join(cur_dir_path, 'data')
userdata_file = os.path.join(data_path, 'userdata.csv')

def get_user_data(userdata):
    api_key = input("Enter api key: ")
    api_secret = input("Enter api secret: ")
    userdata.loc[0, 'api_key'] = api_key
    userdata.loc[0, 'api_secret'] = api_secret
    return userdata
    

def check_data_validity(userdata):
    if userdata.isnull().loc[0,'api_key'] or userdata.isnull().loc[0,'api_secret'] \
                or (not userdata.loc[0, 'api_key'].isalnum()) or (not userdata.loc[0, 'api_secret'].isalnum()):
        print("Provide valid api_key/api_secret")
        print("--------------------------------")
        return False
    return True    


def setup():
    try:
        if (not os.path.exists(data_path)):
            os.makedirs(data_path)
        
        if (not os.path.exists(userdata_file)):
            userdata = pd.DataFrame(
                {
                    "user_id" : [],
                    "user_name" : [],
                    "api_key" : [],
                    "api_secret" : [],
                    "access_token" : [],
                    "public_token" : [],
                    "token_req_date" : []

                })
            userdata = get_user_data(userdata)
            while not check_data_validity(userdata):
                get_user_data(userdata)
            userdata.to_csv(userdata_file, index=False)
        else:
            userdata = pd.read_csv(userdata_file)
            while not check_data_validity(userdata):
                get_user_data(userdata)
            userdata.to_csv(userdata_file, index=False)
    except Exception as e:
        print("** ERROR in setup. Run setup.py again.", e, datetime.datetime.now())
        

def is_valid_token(api_key, access_token):
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        kite.profile()
        return True
    except Exception:
        return False


def generate_token(userdata):
    try:
        api_key = userdata.loc[0, 'api_key']
        api_secret = userdata.loc[0, 'api_secret']

        kite = KiteConnect(api_key=api_key)
        print("Login URL :=>  " + kite.login_url())
        request_token = input("Enter new request token value : ")
        res = kite.generate_session(request_token, api_secret)

        #print(res)
        userdata.loc[0, 'access_token'] = res['access_token']
        userdata.loc[0, 'user_name'] = res['user_name']
        userdata.loc[0, 'user_id'] = res['user_id']
        userdata.loc[0, 'public_token'] = res['public_token']
        userdata.loc[0, 'token_req_date'] = datetime.datetime.now()
        userdata.to_csv(userdata_file, index=False)
    except Exception as e:
        print("** ERROR in Access Token Generation. ", e, datetime.datetime.now())


def validate_access_token():
    try:
        userdata = pd.read_csv(userdata_file)
        api_key = userdata.loc[0, 'api_key']
        access_token = userdata.loc[0, 'access_token']
        
        if not is_valid_token(api_key, access_token):
            raise Exception("Invalid Token")
        else :
            print("Authentication Done")

    except Exception as e:
        print("** ERROR in Access Token Validation. ", e, datetime.datetime.now())
        generate_token(userdata)
        validate_access_token()
            

setup()
validate_access_token()