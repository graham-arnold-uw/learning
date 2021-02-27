import time, logging
import datetime as dt
from collections import defaultdict
import utilities.sql_helpers as sqlh
import utilities.project_helpers as ph
import price_stream.price_stream as ps
from analytics_stream.analytics_engine_params import *
import analytics_stream.analytics_drivers as ad



#create dictionary mapping quotes -> SMA table names -> currency pairs -> average counter (counter to be used when aggregating current average)
def initialize_sma_tree(driver_choices_in):

    driver_choices = dict(driver_choices_in)
    for k in driver_choices.keys():
        choices = driver_choices[k]
        if len(choices) == 0:
            driver_choices[k] = None
        else:
            choices = choices.split(',')
            driver_choices[k] = choices

    sma_tree = {}
    for quote in QUOTE_LIST:
        choices_dict = {}
        for k in driver_choices:

            choices = driver_choices[k]
            if choices != None:
                for c in choices:
                    table_name =  ph.get_sma_table_name(quote,k,c)
                    choices_dict[table_name] = defaultdict(int)

        sma_tree[quote] = choices_dict


    return sma_tree

#returns dict of following structure
#
# {BTC_SMA_30M : {default 0}, LTC_SMA_2H : {default 0}}
#
#
def initialize_analytics_tables(antype, analytics_choices):

    analytics_tables = []

    for quote in QUOTE_LIST:
        #choices_dict = {}
        for k in analytics_choices:
            choices = analytics_choices[k]
            if choices != None:
                for c in choices:
                    table_name = ph.construct_analytics_tablename(quote,antype,k,c)
                    analytics_tables.append(table_name)

    return analytics_tables

def construct_driver_choices():

    with open(ANALYTICS_CHOICES_FILE) as f:
        choices_file = list(f)
        choices_file = [s.rstrip() for s in choices_file]


    i = 0
    choices_dict = defaultdict(dict)
    while i < len(choices_file):
        if i % 4 == 0:
            choice = choices_file[i]
        else:
            inval = choices_file[i]
            tu = inval.split(':')
            if len(tu[1]) == 0:
                tu[1] = None
            else:
                tu[1] = tu[1].split(',')
            choices_dict[choice].update([tu])
        i += 1

    return choices_dict

def print_choice_tables(choices):
    adb = sqlh.create_db_connection(ANALYTICS_DB_NAME, DB_TIMEOUT)
    for table in choices:
        print(table)
        col_names = sqlh.get_column_names(adb,table)
        print(col_names)
        col_vals = sqlh.get_columns(adb, table)
        for col in col_vals:
            print(col)
        print()

    adb.close()


def boot_strap_databases(driver_choices, pdb, adb):

    for quote in QUOTE_LIST:
        price_table_name = ph.construct_prices_tablename(quote)
        col_names = sqlh.get_column_names(pdb, price_table_name)
        col_types = sqlh.get_column_types(pdb, price_table_name)

        for choice in driver_choices:
            choices = driver_choices[choice]
            for itype in choices:
                invlist = choices[itype]
                if invlist != None:
                    for inv in invlist:
                        #table_name = quote + '_SMA_' + inv + ts
                        table_name = ph.construct_analytics_tablename(quote, choice, itype, inv)
                        if not sqlh.check_table_exists(adb, table_name):
                            sqlh.create_table(adb, table_name, col_names, col_types)
                        else:
                            prev_pairs_all = sqlh.get_column_names(adb, table_name)
                            _, *prev_pairs = prev_pairs_all
                            prev_set = set()
                            for pair in prev_pairs_all:
                                prev_set.add(pair)
                            new_set = set()
                            for el in col_names:
                                new_set.add(el)

                            add_cols = ph.find_added_columns(new_set, prev_set)
                            #print(add_cols)
                            for added_pair in add_cols:
                                sqlh.add_column_new(adb, table_name, added_pair, 'REAL')
                                logging.basicConfig(
                                    filename=ANALYTICS_LOG_FILE, format='%(asctime)s - %(message)s')
                                logging.info('%s added to tracking', added_pair)



#create databases if they dont exist
#update analytics database columns if there are new ones
#create analytics tree datastructures for organizing values
#
#input
#   driver choices: dict of SMA interval choices {M: [30, 45], H : [3, 5]}
#
#output
#   list of analytics trees of structure choice-> sma_table_name -> default 0 (to be filled in with currency pairs
def boot_strapper(driver_choices):

    pdb = sqlh.create_db_connection(PRICES_DB_NAME, DB_TIMEOUT)
    adb = sqlh.create_db_connection(ANALYTICS_DB_NAME, DB_TIMEOUT)

    boot_strap_databases(driver_choices, pdb, adb)


    #print()
    #res = sqlh.get_all_tables(adb)
    #test = res[0][0]
    #sqlh.print_column_names(adb,test)
    #print()
    #add data structures for analytics calculations
    analytics_tree = {}

    for choice in driver_choices:
        analytics_tables = initialize_analytics_tables(choice, driver_choices[choice])
        analytics_tree[choice] = analytics_tables
    #sma_tree = initialize_sma_tree(driver_choices)
    #analytics_trees.append(sma_tree)


    adb.close()
    pdb.close()

    return analytics_tree

def update_analytics(analytics_tree):

    #access each analytics subtree
    #identify the interval and slots
    #for each currency pair
    #check if analytics can be generated
    #if so update slot for that pair with result
    #once subtree is populated (entire SMA subtree) go about writing out to DB

    #grab rows from database to satisfy the greatest slots then you can build
    #less slot averages from that data without another db query
    for choice in analytics_tree:
        choice_tables = analytics_tree[choice]

        #print(choice_dict)
        if len(choice_tables) > 0:
            update_analytics_db(choice_tables)

        #print_choice_tables(choice_tables)

        #next process the updated choice dict
        #create a database write function that takes the updated analytics dict

def check_time_range(exp_time, row_time, inval_type):
    if inval_type == 'M':
        delta = ANALYTICS_MISSED_PRICE_M
    elif inval_type == 'H':
        delta = ANALYTICS_MISSED_PRICE_H
    elif inval_type == 'D':
        delta = ANALYTICS_MISSED_PRICE_D
    else:
        raise ValueError

    min_time = exp_time - (delta * 60)

    return True if row_time >= min_time else False


def generate_row_matrix(pdb,quote, inval):
    price_table_name = ph.construct_prices_tablename(quote)
    pdb_cols = sqlh.get_column_names(pdb, price_table_name)
    pdb_len = sqlh.count_rows(pdb, price_table_name)
    row_matrix = []
    debug = []
    inval_num, inval_type = inval[:-1], inval[-1]
    inval_num = int(inval_num)
    inval_iters = inval_num


    if inval_type == 'M':
        gap = 1
        inval_iters = inval_iters // PRICES_UPDATE_INTERVAL
    elif inval_type == 'H':
        gap = 60 // PRICES_UPDATE_INTERVAL
    elif inval_type == 'D':
        gap = 1440 // PRICES_UPDATE_INTERVAL
    else:
        raise ValueError

    num_entries_needed = inval_iters * gap + 1

    if pdb_len < num_entries_needed:
        return pdb_cols, None


    exp_time = time.time()
    curr_row_num = pdb_len
    #print(inval_iters)
    for i in range(inval_iters+1):
        #print(curr_row_num)
        curr_row = sqlh.get_table_row(pdb, price_table_name, curr_row_num)
        row_time = curr_row[0]
        if check_time_range(exp_time, row_time, inval_type):
            row_matrix.append(list(curr_row))
            debug.append([curr_row_num] + list(curr_row))
            exp_time = row_time
        else:
            return pdb_cols, None

        curr_row_num -= gap
        exp_time -= gap * PRICES_UPDATE_INTERVAL * 60

    #if inval_type == 'H':
    #    with open('hour_write.txt', 'a+') as f:
    #        for r in row_matrix:
    #            line = str(r) + '\n'
    #            f.write(line)
    #        f.write('\n')
    #for r in debug:
    #    print(r)
    return pdb_cols, row_matrix


def analytics_factory(choice):
    if choice == 'SMA':
        return ad.sma_driver
    elif choice == 'EMA':
        return ad.ema_driver
    else:
        raise ValueError

def update_analytics_db(analytics_tables):
    #dont forget to reset quote_dict before writing out new keys
    pdb = sqlh.create_db_connection(PRICES_DB_NAME, DB_TIMEOUT)
    adb = sqlh.create_db_connection(ANALYTICS_DB_NAME, DB_TIMEOUT)

    #print('h')

    for table in analytics_tables:
        quote, choice, inval = table.split('_')

        #check if new columns are needed in analytics table
        added_cols = sqlh.check_for_new_cols(adb, table, pdb, ph.construct_prices_tablename(quote))
        for added_pair in added_cols:
            sqlh.add_column_new(adb, table, added_pair, 'REAL')

        #create row_matrix and keep track of pdb column order for later use
        #print('h2')
        pdb_cols, row_matrix = generate_row_matrix(pdb, quote, inval)
        #print(row_matrix)
        #print()
        #for r in row_matrix:
        #    print(r)
        #if row_matrix is None that means that there isn't enough data in the DB
        # to produce the required interval
        if row_matrix == None:
            continue

        analytics_func = analytics_factory(choice)

        #pull off time col from row_matrix, save latest time
        latest_time = row_matrix[0][0]

        #remove timestamp column
        for i in range(len(row_matrix)):
            row_matrix[i].pop(0)
            #print(row_matrix[i])
       # print()
        analytics_vector = analytics_func(row_matrix) #make sure analytics func keep latest timestamp
        analytics_vector = [latest_time] + analytics_vector
        #print(pdb_cols)
        #print(analytics_vector)
        #print(len(pdb_cols) == len(analytics_vector))
        #print()
        sqlh.insert_row(adb,table, pdb_cols, analytics_vector)



    adb.close()
    pdb.close()



#Main loop, runs at the same interval at the price stream but offset by 1 minute
#
#input
#   analytics trees
#
#output
#   writes out updates to the price_analytics.db if available
def analytics_loop(analytics_trees):
    done = False
    while(1):

        #don't need loop to update super fast
        #analytics are at a minimum performed at on minute time interavls
        time.sleep(ANALYTICS_LOOP_DELAY)
        curr_time = dt.datetime.now()

        curr_min = curr_time.minute

        if curr_min % PRICES_UPDATE_INTERVAL == 1 and not done:
            #ps.update_prices()
            #sqlh.update_row(db,PRICES_LU_TABLE,PRICES_LU_COL, int(tim.time()),1)
            update_analytics(analytics_trees)
            done = True

        if curr_min % PRICES_UPDATE_INTERVAL != 1:
            done = False






if __name__ == '__main__':

    #change driver_choices to make it a dict of {'SMA' : {H: [1,2]} 'EMA' : {H:[1,2]}
    driver_choices = construct_driver_choices()
    #print(driver_choices)
    #print()
    analytics_tree = boot_strapper(driver_choices)
    #print(analytics_tree)
    #print()
    analytics_loop(analytics_tree)
