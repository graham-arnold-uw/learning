import price_stream as ps
from analytics_engine_params import *
import time
import sql_helpers as sqlh
import datetime as dt











def boot_strapper():
    last_price_update = time.time()

    db = sqlh.create_db_connection(PRICES_DB_NAME, ps.DB_TIMEOUT)

    if not sqlh.check_table_exists(db,PRICES_LU_TABLE):
        sqlh.create_table(db, PRICES_LU_TABLE, PRICES_LU_COL, 'INTEGER')
        sqlh.insert_row(db, PRICES_LU_TABLE, PRICES_LU_COL, int(time.time()))


    #sqlh.print_columns(db,PRICES_LU_TABLE)


def update_analytics():

    




def analytics_loop():

    while(1):

        #don't need loop to update super fast
        #analytics are at a minimum performed at on minute time interavls
        time.sleep(ANALYTICS_LOOP_DELAY)
        curr_time = dt.datetime.now()

        curr_min = curr_time.minute

        if curr_min % PRICES_UPDATE_INTERVAL == 0:
            ps.update_prices()
            #sqlh.update_row(db,PRICES_LU_TABLE,PRICES_LU_COL, int(tim.time()),1)
            update_analytics()






if __name__ == '__main__':
    #boot_strapper()
    analytics_loop()
