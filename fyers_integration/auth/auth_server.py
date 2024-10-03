import webbrowser

from json_util import get_json_value
from datetime import datetime

from flask import Flask, json, request

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
        update_auth_code(auth_code)

        return "AuthCode Generated Successfully. ##### You can close this #####"

    return "Error"


def update_auth_code(auth_code):
    with open('/Users/debanshu.rout/repo/external/algotrading/fyers_integration/data/token.json', 'r+') as f:
        data = json.load(f)
        data['auth_code'] = auth_code  # <--- add `id` value.
        data['update'] = "1"  # <--- add `id` value.
        data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # remove remaining part


app.run(host='localhost', port=27070)
