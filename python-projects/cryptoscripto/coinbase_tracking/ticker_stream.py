from ticker_list import ticker_choices
from coinbase_api_params import *
from coinbase_auth import *

import json, hmac, hashlib, time, requests, codecs, base64,sys, os.path, csv, time


def get_ticker_url(prod_id):
    return 'products/' + prod_id + '/ticker'

def get_ticker(prod_id):

    prod_tick = requests.get(API_URL + get_ticker_url(prod_id))
    #prod_tick = requests.get('https://api.pro.coinbase.com/products/BTC-USD/ticker')
    tick_json = prod_tick.json()
    return tick_json

def write_tick(csv_path, tick, pair):
    price = tick['price']
    time_stamp = tick['time']
    volume = tick['volume']

    if os.path.isfile(csv_path):
        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow([time_stamp, pair, price, volume])
    else:
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Time Stamp','Currency Pair','Price','Volume'])
            writer.writerow([time_stamp, pair, price, volume])

def poll_prices(ticker_choices):
    base_path = os.path.dirname(os.path.realpath(__file__))
    data_path = 'tick_data'

    for choice in ticker_choices:
        base, quote = choice.split('-')
        csv_name = base + '_' + quote + '.csv'
        csv_path = os.path.join(base_path, data_path, csv_name)
        choice_tick = get_ticker(choice)
        #print(choice)
        #print(choice_tick)
        #print(csv_path)
        write_tick(csv_path, choice_tick, choice)
        time.sleep(POLL_DELTA)

if __name__ == '__main__':
    poll_prices(ticker_choices)
