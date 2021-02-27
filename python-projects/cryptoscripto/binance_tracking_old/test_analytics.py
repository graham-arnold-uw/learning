import sqlite3
import sql_helpers as sqlh
from trading_pairs_params import *
from analytics_engine_params import *
import analytics_engine as ae

def run_test(pdb,adb):
    tables = sqlh.get_all_tables(adb)
    #sqlh.print_columns_formatted(db,'BTC_prices')
    for table in tables:
        quote, choice, inval = table.split('_')

        last_a_row = sqlh.last_n_rows(adb, table, 1)
        pdb_cols, row_matrix = ae.generate_row_matrix(pdb, quote, inval)

        analytics_func = ae.analytics_factory(choice)

        #pull off time col from row_matrix, save latest time
        latest_time = row_matrix[0][0]

        #remove timestamp column
        for i in range(len(row_matrix)):
            row_matrix[i].pop(0)
            #print(row_matrix[i])
       # print()
        # make sure analytics func keep latest timestamp
        analytics_vector = analytics_func(row_matrix)
        analytics_vector = [latest_time] + analytics_vector
        print(analytics_vector)
        print(last_a_row)

if __name__ == '__main__':
    pdb = sqlh.create_db_connection(PRICES_TABLE_NAME, DB_TIMEOUT)
    adb = sqlh.create_db_connection(ANALYTICS_DB_NAME,DB_TIMEOUT)
    
    tables = sqlh.get_all_tables(adb)
    #print(tables)
    #sqlh.print_columns_formatted(db,'BTC_prices')
    res = sqlh.last_n_rows(adb, 'BTC_SMA_3H', 10)
    for row in res:
        print(row)
        print()
        print()

    print(sqlh.count_rows(adb, 'BTC_SMA_3H'))
    

