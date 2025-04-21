import webbrowser

import requests

from json_util import get_json_value, update_json_key
from datetime import datetime

from flask import Flask, json, request

from fyers_apiv3 import fyersModel

app = Flask(__name__)


@app.route('/', methods=['GET'])
def ping():
    return "Welcome to Algotrading"


@app.route('/login', methods=['GET'])
def login():
    client_id = get_json_value('client_id')
    redirect_uri = get_json_value('redirect_uri')
    state = get_json_value('state')

    # Construct the URL
    base_url = "https://api-t1.fyers.in/api/v3/generate-authcode"
    response_type = "code"

    generated_url = f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&state={state}"

    print(generated_url)

    # Open the generated URL in the default web browser
    webbrowser.open(generated_url)
    return generated_url


@app.route('/generate-authcode', methods=['GET'])
def get_auth_code():
    args = request.args
    auth_code = args["auth_code"]

    if args['s'] == 'ok' and (args['state'] == get_json_value('state')):
        update_json_key('auth_code', auth_code)
        update_json_key('update', '1')  # <--- add `id` value.
        update_json_key('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        status = generate_token()
        if status != 'error':
            return "AuthCode & Access Token Generated Successfully. ##### You can close this #####"

    return "error"


@app.route('/refresh-token', methods=['GET'])
def refresh_token():
    client_id = get_json_value('client_id')
    secret_key = get_json_value('secret_key')
    refresh_token = get_json_value('refresh_token')
    pin = get_json_value('pin')

    grant_type = "refresh_token"
    url = 'https://api-t1.fyers.in/api/v3/validate-refresh-token'

    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
    )

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "grant_type": grant_type,
        "appIdHash": session.get_hash().hexdigest(),
        "refresh_token": refresh_token,
        "pin": pin
    }


    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response)
    if response.status_code == 200:
        response_data = response.json()
        update_json_key('access_token', response_data.get('access_token'))
        return "Token Refresh Successful"
    else:
        return "error"



def generate_token():
    client_id = get_json_value('client_id')
    secret_key = get_json_value('secret_key')
    redirect_uri = get_json_value('redirect_uri')
    response_type = "code"
    grant_type = "authorization_code"

    auth_code = get_json_value('auth_code')

    # Create a session object to handle the Fyers API authentication and token generation
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type=response_type,
        grant_type=grant_type
    )

    session.set_token(auth_code)
    response = session.generate_token()
    print(response)
    if response['s'] == 'ok':
        update_json_key('access_token', response['access_token'])
        update_json_key('refresh_token', response['refresh_token'])
        return "Access Token Generation Successful"
    else:
        return "error"


app.run(host='localhost', port=27070)
