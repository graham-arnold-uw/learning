#Author: Graham Arnold
#Date created: 8/20/20
#Date revise:
#
#This module retrieves all the currently available trading pairs with a specified quote currency
# from the binance API and writes them to a file
import sqlite3, json, requests, sys, os.path, csv, getpass
from urllib.parse import urljoin
from utilities.binance_helper import BinanceException
from utilities import sql_helpers as sqlh
from price_stream.trading_pairs_params import *

username = getpass.getuser()
keypath = ['/home', username, 'Desktop', 'keys','binance']
path = os.path.join(*keypath)
sys.path.append(path)
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






#    c.execute('PRAGMA table_info(symbols)')
#    for r in c:
#        print(r)

def fill_symbol_table(db, table_name, quote_tup):
    c = db.cursor()
    #ret = True
    for quote in quote_tup:
        quote_pairs = poll_pairs(quote)
        l = len(quote_pairs)
        #print(l)
        for pair in quote_pairs:
            cmd = f'INSERT INTO {table_name}({quote}) VALUES(?)'
            vals = [pair]
            c.execute(cmd, vals)

        #cmd2 = f'SELECT COUNT(*) from {table_name} WHERE {quote}'
        cmd2 = f'SELECT COUNT({quote}) from {table_name}'
        c.execute(cmd2)
        res = c.fetchall()
        #print(res[0][0])
        if res[0][0] != l:
            raise Exception('fill operation failed')
        #base_list, = filter_bases(quote_pairs, quote)
        #quote_list = filter_quotes(quote_pairs, quote)
        #split_tuple = split_pairs(quote_pairs, quote)
    db.commit()
    #return ret
        #print(quote_pairs)
        #print()
        #print(split_tuple)


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


    db = sqlh.create_db_connection(DB_NAME, DB_TIMEOUT)

    sqlh.delete_table(db, SYMBOL_TABLE_NAME)

    #r2 = sqlh.check_table_exists(db, SYMBOL_TABLE_NAME)

    #print(r2)


    sqlh.create_table(db, SYMBOL_TABLE_NAME, QUOTE_LIST, COL_TYPES)
    #r3 = sqlh.check_table_exists(db, SYMBOL_TABLE_NAME)

    #print(r3)
    #sqlh.print_column_names(db, SYMBOL_TABLE_NAME)

    #sqlh.print_columns(db,SYMBOL_TABLE_NAME)




    #sqlh.print_column_names(db, SYMBOL_TABLE_NAME)

    #create_db_table(db, SYMBOL_TABLE_NAME, QUOTE_LIST)

    #sqlh.get_all_tables(db)

    fill_symbol_table(db, SYMBOL_TABLE_NAME, QUOTE_LIST)
    #sqlh.print_columns(db,SYMBOL_TABLE_NAME)

    #slqh.print_table(db, SYMBOL_TABLE_NAME)

    db.close()
    #check if symbols table already exists
    #c.execute('SELECT count(name) FROM sqlite_master WHERE type= ? AND name = ?', ('table',SYMBOL_TABLE_NAME))
    #if not c.fetchone()[0]:
        #create_db_table(c, SYMBOL_TABLE_NAME, BASE_LIST)















if __name__ == '__main__':
    update_trading_pairs()
