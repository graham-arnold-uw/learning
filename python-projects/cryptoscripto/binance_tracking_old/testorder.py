import time
import json
import hmac
import hashlib
import requests
import sys
import binance_helper
from urllib.parse import urljoin, urlencode

sys.path.append('/home/graham/Desktop/keys/binance')
from testkey1 import API_KEY
from testkey1 import API_SECRET

BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}

def testOrderCreate():
    #test create new order
    PATH = '/api/v3/order/test'
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': 'ETHUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': 0.1,
        'price': 500.0,
        'recvWindow': 5000,
        'timestamp': timestamp
    }

    query_string = urlencode(params)
    params['signature'] = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = urljoin(BASE_URL, PATH)
    r = requests.post(url, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())


if __name__ == '__main__':
    testOrderCreate()
