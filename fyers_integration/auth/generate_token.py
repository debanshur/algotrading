import json
import random
import string
import threading
import time

import requests
from fyers_api import accessToken
import webbrowser

from json_util import update_json_key, get_json_value

redirect_uri = "http://localhost:27070/"
client_id = "SLWIS8N2SP-100"
secret_key = "286AWK1K2I"
grant_type = "authorization_code"


response_type = "code"

res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=6))

state = res

update_json_key('state', res)
update_json_key('update', "0")

appSession = accessToken.SessionModel(client_id=client_id, redirect_uri=redirect_uri, response_type=response_type,
                                      state=state, secret_key=secret_key, grant_type=grant_type)

generateTokenUrl = appSession.generate_authcode()

print((generateTokenUrl))
webbrowser.open(generateTokenUrl, new=1)

while(get_json_value('update') == "0"):
    print("waiting...")
    time.sleep(1)

auth_code = get_json_value('auth_code')

appSession.set_token(auth_code)
response = appSession.generate_token()

try:
    access_token = response["access_token"]
except Exception as e:
    print(e,
          response)

print("access_token:")
print(access_token)

update_json_key('access_token', access_token)

