from flask import Flask, json, request

from json_util import get_json_value

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_auth_code():
    args = request.args
    auth_code = args["auth_code"]

    if args['state'] == get_json_value('state'):
        update_auth_code(auth_code)

        return "Auth Successfull"

    return "Error"


def update_auth_code(auth_code):
    with open('/Users/debanshu.rout/repo/external/algotrading/fyers_integration/data/token.json', 'r+') as f:
        data = json.load(f)
        data['auth_code'] = auth_code  # <--- add `id` value.
        data['update'] = "1"  # <--- add `id` value.
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # remove remaining part


app.run(host='localhost', port=27070)
