#Author: Graham Arnold
#Date created: 8/20/20
#Date revise:
#
#This module retrieves all the currently available trading pairs with a specified quote currency
# from the binance API and writes them to a file
import json, requests, sys, os.path, csv
from binance_helper import BinanceException
from trading_pairs_params import *
from urllib.parse import urljoin
import sqlite3

sys.path.append('/home/graham/Desktop/keys/binance')
from testkey1 import API_KEY

BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}


def filter_pairs(pairs, quote):
    pairs_filtered = [curr_pair for curr_pair in pairs if curr_pair.endswith(quote)]
    return pairs_filtered

def filter_bases(pairs, quote):
    length = len(quote)
    base_filtered  = [curr_pair[:-length] for curr_pair in pairs]
    return base_filtered

def filter_quotes(pairs, quote):
    length = len(quote)
    quote_filtered  = [curr_pair[-length:] for curr_pair in pairs]
    return quote_filtered

def split_pairs(pairs, quote):
    length = len(quote)
    split_tuple  = [(curr_pair[:-length], curr_pair[-length:]) for curr_pair in pairs]
    return split_tuple

def create_db_connection(name, to):
    try:
        db = sqlite3.connect(name, timeout=to)
        #print('connection success')
    except Exception as e:
        print('An error has occured connecting to the database: ', e)
    return db

def create_db_table(db, name, col_tup):
    cmd_string = 'CREATE TABLE IF NOT EXISTS ' + SYMBOL_TABLE_NAME + \
                        ' (' + ','.join(col_tup) + ')'
    c = db.cursor()
    c.execute(cmd_string)
    db.commit()

#    c.execute('PRAGMA table_info(symbols)')
#    for r in c:
#        print(r)

def fill_db_table(db, table, quote_tup):
    c = db.cursor()

    for quote in quote_tup:
        quote_pairs = poll_pairs(quote)
        #base_list, = filter_bases(quote_pairs, quote)
        #quote_list = filter_quotes(quote_pairs, quote)
        split_tuple = split_pairs(quote_pairs, quote)

        print(quote_pairs)
        print()
        print(split_tuple)


def get_all_pairs():
    # Get Price
    PATH = '/api/v3/exchangeInfo'
    params = None

    sym_pairs = []

    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        exch_info = r.json()
        symbols= exch_info['symbols']
        for pair in symbols:
            curr_sym = pair["symbol"]
            sym_pairs.append(curr_sym)

        return sym_pairs

    else:
        raise BinanceException(status_code=r.status_code)



def write_pairs(file_path, pairs):

    with open(file_path, 'w', newline='') as file:
        #writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for pair in pairs:
            file.write(pair + '\n')


def poll_pairs(quote):
    #pairs_dir = 'trading_pairs'
    #file_name = 'current_pairs.txt'
    #base_path = os.path.dirname(os.path.realpath(__file__))

    #sym_path = os.path.join(base_path, pairs_dir, file_name)

    all_pairs = get_all_pairs()
    btc_pairs = filter_pairs(all_pairs,quote)
    return btc_pairs
    #write_pairs(sym_path, btc_pairs)

#main loop function for updating the trading pairs in the database
def update_trading_pairs():


    db = create_db_connection(DB_NAME, DB_TIMEOUT)

    create_db_table(db, SYMBOL_TABLE_NAME, COL_LIST)

    fill_db_table(db, SYMBOL_TABLE_NAME, QUOTE_LIST)

    db.close()
    #check if symbols table already exists
    #c.execute('SELECT count(name) FROM sqlite_master WHERE type= ? AND name = ?', ('table',SYMBOL_TABLE_NAME))
    #if not c.fetchone()[0]:
        #create_db_table(c, SYMBOL_TABLE_NAME, BASE_LIST)















if __name__ == '__main__':
    update_trading_pairs()
