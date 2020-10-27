import sqlite3
import sql_helpers as sqlh
from trading_pairs_params import *

if __name__ == '__main__':
    db = sqlh.create_db_connection(DB_NAME, DB_TIMEOUT)

    #sqlh.print_columns_formatted(db,'BTC_prices')
    res = sqlh.last_n_rows(db,'BTC_prices', 10)
    for row in res:
        print(row)
        print()
        print()

    print(sqlh.count_rows(db,'BTC_prices'))
