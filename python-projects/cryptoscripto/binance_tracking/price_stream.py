#Author: Graham Arnold
#Date: 8/18/20
#price_stream.py: This module pulls price data from binance and regular intervals and stores the historical data in a database
#


import time
import json
import hmac
import hashlib
import requests
import sys, os.path
from binance_helper import BinanceException
from urllib.parse import urljoin, urlencode

sys.path.append('/home/graham/Desktop/keys/binance')
from testkey1 import API_KEY

BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}


#Get Server Time Diff
def getServerTimeDiff():
    PATH =  '/api/v1/time'
    params = None

    timestamp = int(time.time() * 1000)

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, params=params)
    if r.status_code == 200:
        # print(json.dumps(r.json(), indent=2))
        data = r.json()
        print(f"diff={timestamp - data['serverTime']}ms")
    else:
        raise BinanceException(status_code=r.status_code)

def getPrice(symbol):
    # Get Price
    PATH = '/api/v3/ticker/price'
    params = {
        'symbol': symbol
    }

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        raise BinanceException(status_code=r.status_code)

def load_pairs(path):

    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("trading pairs file does not exist.")

    pairs = [line.rstrip() for line in lines]
    print(pairs)




if __name__ == '__main__':
    #getServerTimeDiff()
    #getPrice('BTCUSDT')
    base_path = os.path.dirname(os.path.realpath(__file__))
    pairs_dir = 'trading_pairs'
    file_name = 'current_pairs.txt'
    sym_path = os.path.join(base_path, pairs_dir, file_name)
    load_pairs(sym_path)
