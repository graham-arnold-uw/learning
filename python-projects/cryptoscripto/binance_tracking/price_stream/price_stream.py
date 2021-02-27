#Author: Graham Arnold
#Date: 8/18/20
#price_stream.py: This module pulls price data from binance and regular intervals and stores the historical data in a database
#

import time
import datetime as dt
import json
import hmac
import hashlib
import requests
import sys, os.path
import utilities.sql_helpers as sqlh
import utilities.project_helpers as ph
from utilities.binance_helper import BinanceException
from . import trading_pairs as tp
from .trading_pairs_params import *

from urllib.parse import urljoin, urlencode


import getpass
username = getpass.getuser()
keypath = ['/home', username, 'Desktop', 'keys','binance']
path = os.path.join(*keypath)
sys.path.append(path)
from testkey1 import API_KEY


BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}


def get_exchange_info():
    PATH = '/api/v3/exchangeInfo'
    params = None
    url = urljoin(BASE_URL, PATH)

    r = requests.get(url, params=params)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
        #data = r.json()
        #print(data['rateLimits'])
    else:
        raise BinanceException(status_code=r.status_code)

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

#def mark_time(db, table='Last Update'):
#    c = db.cursor()
#
 #   sqlh.create_table(db,table,'Last Update Time')


def get_prices_old(pairs):
    # Get Price
    res = []
    PATH = '/api/v3/ticker/price'
    #pairs2 = ['LTCBTC']
    for pair in pairs:

        params = {
            'symbol': pair
        }

        url = urljoin(BASE_URL, PATH)
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            #print(json.dumps(r.json(), indent=2))
            data = r.json()
            #print(r.json())
            #print(r.headers)
            res.append(data['symbol'] + ": " + data['price'])
        elif r.status_code == 429:
            print("hit here")
            time.sleep(5)
            r2 = requests.get(url, headers=headers, params=params)
            if r2.status_code != 200:
                raise BinanceException(status_code=r.status_code)
            data = r2.json()
            res.append(data['symbol'] + ": " + data['price'])
        else:
            raise BinanceException(status_code=r.status_code)
        time.sleep(REQUESTS_LIM)
    return res

def get_prices(pairs):
    # Get Price
    syms = []
    prices = []
    PATH = '/api/v3/ticker/price'
    params = None

    pairs = set(pairs)
    #price_dict = dict(zip(pairs, [None]*len(pairs)))

    url = urljoin(BASE_URL, PATH)

    for i in range(30):
        try:
            r = requests.get(url, headers=headers, params=params)
        except:
            time.sleep(60)
        else:
            break
    else:
        raise ConnectionError

    if r.status_code == 200:
        #print(json.dumps(r.json(), indent=2))
        data = r.json()
        #print(json.dumps(data, indent=2))
    else:
        raise BinanceException(status_code=r.status_code)

    for pair in data:
        curr_sym = pair['symbol']
        if curr_sym in pairs:
            #price_dict[curr_sym] = float(pair['price'])
            syms.append(curr_sym)
            prices.append(pair['price'])
    #pairs2 = ['LTCBTC']
    return syms, prices

def load_pairs(db, table_name):

    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("trading pairs file does not exist.")

    pairs = [line.rstrip() for line in lines]
    print(pairs)

def update_time_table(db,table_name, col_name, time):
    c = db.cursor()
    time = [time]
    #cmd = f'DELETE FROM {table_name}'
    fr_exists = sqlh.row_exists(db,table_name,1)
    if fr_exists:
        cmd = f"UPDATE {table_name} SET {col_name} = ? LIMIT 1"
    else :
        cmd = f"INSERT INTO {table_name}({col_name}) VALUES(?)"
    c.execute(cmd, time)
    #cmd2 = f"UPDATE {table_name} SET {col_name} = ? LIMIT 1"
    #cmd = "UPDATE last_update SET symbols = 'hello'"
    #print(cmd)
    #c.execute(cmd)

    #cmd = f'INSERT INTO last_update({col_name}) VALUES(?)'
    #c.execute(cmd2,time)
    db.commit()

#finish this
#need to make way to take in columns and values and apply them
#need to make string constructor
def update_active_table(db,table_name, added, deleted):
    #c = db.cursor()
    #time = [time]
    #cmd = f'DELETE FROM {table_name}'

    for new_pair in added:
        sqlh.add_column_new(db, table_name,new_pair, 'INTEGER')
        sqlh.update_row(db, table_name, new_pair, 1, 1)

    for del_pair in deleted:
        print(del_pair)
        sqlh.update_row(db, table_name, del_pair, 0, 1)

    #fr_exists = sqlh.row_exists(db,table_name,1)
    #if fr_exists:
    #    cmd = f"UPDATE {table_name} SET {col_name} = ? LIMIT 1"
    #else :
    #    cmd = f"INSERT INTO {table_name}({col_name}) VALUES(?)"
    #c.execute(cmd, time)
    #cmd2 = f"UPDATE {table_name} SET {col_name} = ? LIMIT 1"
    #cmd = "UPDATE last_update SET symbols = 'hello'"
    #print(cmd)
    #c.execute(cmd)

    #cmd = f'INSERT INTO last_update({col_name}) VALUES(?)'
    #c.execute(cmd2,time)
    #db.commit()

def initialize(db):
    #sqlh.delete_table(db,SYMBOL_TABLE_LU_NAME)
    if not sqlh.check_table_exists(db, SYMBOL_TABLE_LU_NAME):
        sqlh.create_table(db, SYMBOL_TABLE_LU_NAME, TIME_COL, TIME_COL_TYPES)
        curr_time = str(int(time.time()))
        sqlh.insert_row(db, SYMBOL_TABLE_LU_NAME, TIME_COL, curr_time)
        tp.update_trading_pairs()

    else:
        curr_time = str(int(time.time()))

        prev_times = sqlh.first_n_rows(db, SYMBOL_TABLE_LU_NAME)
        #print(prev_times)
        sym_prev = prev_times[0][0]
        #print(int(curr_time) - int(sym_prev))
        if (int(curr_time) - int(sym_prev)) > SECONDS_PER_DAY:
            #print('hit')
            tp.update_trading_pairs()
            #update_time_table(db, SYMBOL_TABLE_LU_NAME, SYMBOL_TABLE_NAME,curr_time)
            sqlh.update_row(db, SYMBOL_TABLE_LU_NAME, TIME_COL, curr_time, 1)
    #sqlh.delete_table(db,'last_update')
    #sqlh.create_table(db, SYMBOL_TABLE_LU_NAME, TIME_COL, TIME_COL_TYPES)
    #sqlh.create_table(db, PRICES_TABLE_NAME)
    #sqlh.print_column_names(db,SYMBOL_TABLE_LU_NAME)
    #tp.update_trading_pairs()

    #update_time_table(db,'last_update',SYMBOL_TABLE_NAME,curr_time)
    #update_time_table(db,'last_update',SYMBOL_TABLE_NAME,curr_time)
    #update_time_table(db,'last_update',PRICES_TABLE_NAME,curr_time)
    #sqlh.print_columns(db,SYMBOL_TABLE_LU_NAME)
    #sqlh.print_column_names(db,'last_update')
    #print(sqlh.row_exists(db,'last_update',1))
    #print(sqlh.row_exists(db,'symbols',1))




def update_prices():

    #update all symbols in the prices.db
    #tp.update_trading_pairs()

    db = sqlh.create_db_connection(DB_NAME, DB_TIMEOUT)
    initialize(db)
    #syms = sqlh.get_columns(db,SYMBOL_TABLE_NAME)

    sym_cols = sqlh.split_columns(db,SYMBOL_TABLE_NAME)

    #print(sym_cols)
    #sqlh.delete_table(db,'BTC_prices')
    #sqlh.delete_table(db,'BTC_prices_active')
    #main loop through each quote currency
    #initialize prices tables for each quote if not existing
    #update each quote table's syms col for any new syms
    for idx, quote in enumerate(QUOTE_LIST):
        quote_table = quote + '_prices'
        quote_table_active = quote_table + '_active'
        #print(quote_table)
        cols = sym_cols[idx+1]
        #print(cols)
        #create prices table if it doesn't exist
        if not sqlh.check_table_exists(db,quote_table):
            #cols = sym_cols[idx+1]
            num_cols = len(cols)
            actv = [1]*(num_cols+1)
            col_types = tuple(['INTEGER'] + ['REAL'] * num_cols)
            col_types_active = tuple(['INTEGER'] * (num_cols + 1))
            cols_in = tuple(['Timestamp'] + list(cols))
            #print('hit')
            #print(col_types)
            #print(cols_in)
            sqlh.create_table(db,quote_table,cols_in,col_types)
            if not sqlh.check_table_exists(db, quote_table_active):
                sqlh.create_table(db,quote_table_active,cols_in,col_types_active)
                sqlh.insert_row(db,quote_table_active,cols_in,actv)
        #else if table does exists need to look to see if any new currency pairs added
        # if any new pairs added need to add new column
        else:
            #cols = sym_cols[i]
            prev_pairs_all = sqlh.get_column_names_old(db, quote_table)
            _, *prev_pairs = prev_pairs_all
            prev_set = set()
            for pair in prev_pairs:
                prev_set.add(pair[0])
            new_set = set(cols)
            #new_len = len(new_set)
            #prev_len = len(prev_set)

            #del_cols = find_deleted_columns(new_set,prev_set)
            #print(del_cols)
            add_cols = ph.find_added_columns(new_set,prev_set)
            if len(add_cols) > 0:
                with open(PRICE_STREAM_LOG, 'a+') as f:
                    f.write('**********************************\n')
                    f.write('Adding columns: \n')
                    f.write(str(add_cols) + '\n')
                    f.write('\n')
                    f.write('Old Set \n')
                    f.write(str(prev_set))
                    f.write('\n')
                    f.write('New Set \n')
                    f.write(str(new_set))
                    f.write('\n')
                    f.write('**********************************\n')

            #print(add_cols)
            #update_active_table(db, quote_table_active, add_cols, del_cols)

            #add new column to the prices table now
            for added_pair in add_cols:
                sqlh.add_column_new(db, quote_table, added_pair, 'REAL')

        quote_pairs = sqlh.get_column_names_old(db, quote_table)
        timestamp, *pairs_cleaned = [pair_tup[0] for pair_tup in quote_pairs]
        #print(pairs_cleaned)
        #print(timestamp)
        #get_exchange_info()
        pairs, prices = get_prices(pairs_cleaned)
        #for i, item in enumerate(pairs):
        #   print(item + ": " + str(prices[i]))
        curr_time = str(int(time.time()))
        ###sym = prices
        price_cols = [timestamp] + pairs
        row_vals = [curr_time] + prices
        #print(price_cols)
        #print(row_vals)

        sqlh.insert_row(db, quote_table, price_cols, row_vals)
        #sqlh.print_columns_formatted(db,quote_table)
        #prevcd_times = sqlh.first_n_rows(db,'last_update')


        #sqlh.print_column_names(db,quote_table)
        #sqlh.print_column_names(db,quote_table_active)
        #sqlh.print_columns(db,quote_table)
        #sqlh.print_columns(db,quote_table_active)
        #print(sqlh.get_row(db,quote_table_active, 'rowid', 1))

    db.close()


def price_stream_loop():
    done = False
    while(1):

        #don't need loop to update super fast
        #analytics are at a minimum performed at on minute time interavls
        time.sleep(30)
        curr_time = dt.datetime.now()

        curr_min = curr_time.minute

        if curr_min % PRICES_UPDATE_INTERVAL == 0 and done == False:
            update_prices()
            done = True
            #print(time.time())
            #sqlh.update_row(db,PRICES_LU_TABLE,PRICES_LU_COL, int(tim.time()),1)
            #update_analytics()

        elif curr_min % PRICES_UPDATE_INTERVAL == 1:
            done = False

if __name__ == '__main__':
    #getServerTimeDiff()
    #getPrice('BTCUSDT')
    #base_path = os.path.dirname(os.path.realpath(__file__))
    #pairs_dir = 'trading_pairs'
    #file_name = 'current_pairs.txt'
    #sym_path = os.path.join(base_path, pairs_dir, file_name)
    price_stream_loop()
