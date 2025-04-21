import json

import requests
from fyers_api import accessToken
from fyers_api import fyersModel
import webbrowser

"""
In order to get started with Fyers API we would like you to do the following things first.
1. Checkout our API docs :   https://myapi.fyers.in/docs/
2. Create an APP using our API dashboard :   https://myapi.fyers.in/dashboard/
Once you have created an APP you can start using the below SDK 
"""

#### Generate an authcode and then make a request to generate an accessToken (Login Flow)

"""
1. Input parameters
"""

#PASS = Fyers@12345
#redirect_uri = "https://localhost:20202"  ## redircet_uri you entered while creating APP.
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
client_id = "9UZA9YK19H-100"  ## Client_id here refers to APP_ID of the created app
secret_key = "22IP9FRBOT"  ## app_secret key which you got after creating the app
grant_type = "authorization_code"  ## The grant_type always has to be "authorization_code"
response_type = "code"  ## The response_type always has to be "code"
state = "samplea"  ##  The state field here acts as a session manager. you will be sent with the state field after successfull generation of auth_code

### Connect to the sessionModel object here with the required input parameters
appSession = accessToken.SessionModel(client_id=client_id, redirect_uri=redirect_uri, response_type=response_type,
                                      state=state, secret_key=secret_key, grant_type=grant_type)



### Make  a request to generate_authcode object this will return a login url which you need to open in your browser from where you can get the generated auth_code
generateTokenUrl = appSession.generate_authcode()

"""There are two method to get the Login url if  you are not automating the login flow
1. Just by printing the variable name 
2. There is a library named as webbrowser which will then open the url for you without the hasel of copy pasting
both the methods are mentioned below"""
print((generateTokenUrl))
webbrowser.open(generateTokenUrl, new=1)

#eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE2NTYxNDU3MzAsImV4cCI6MTY1NjE3NTczMCwibmJmIjoxNjU2MTQ1MTMwLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImF1dGhfY29kZSIsImRpc3BsYXlfbmFtZSI6IlhEMTE4NTAiLCJub25jZSI6IiIsImFwcF9pZCI6IjlVWkE5WUsxOUgiLCJ1dWlkIjoiNjlhNWQ1YWQ5NjEzNDk0ZTk4ZjUzMjVhZTk1NTBjNTciLCJpcEFkZHIiOiI0OS4zNy4xNjMuMTUxIiwic2NvcGUiOiIifQ.fCet3kjwSYkSE5ndkerIuVtgT0XQ2sad262rpxUGfFU




