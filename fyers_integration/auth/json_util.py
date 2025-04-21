import json


def get_json_value(key):
    with open('/Users/debanshu.rout/repo/external/algotrading/fyers_integration/data/token.json', 'r+') as f:
        data = json.load(f)
        return data[key]


def update_json_key(key, value):
    with open('/Users/debanshu.rout/repo/external/algotrading/fyers_integration/data/token.json', 'r+') as f:
        data = json.load(f)
        data[key] = value  # <--- add `id` value.
        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()
