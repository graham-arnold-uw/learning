import price_stream as ps
from analytics_engine_params import *
import time
import sql_helpers as sqlh
import datetime as dt
import analytics_drivers as ad





def boot_strap_databases(driver_choices,pdb, adb):
    
    for quote in QUOTE_LIST:
        price_table_name = quote + '_prices'
        price_cols = sqlh.get_column_names(pdb, price_table_name)
        price_col_types = sqlh.get_column_types(pdb, price_table_name)

        col_names = [col[0] for col in price_cols]
        col_types = [ctype[0] for ctype in price_col_types]  

        for ts, invlist in driver_choices:
            invs = invlist.split(',')
            for inv in invs:
                table_name = quote + '_SMA_' + inv + ts
                if not sqlh.check_table_exists(adb,table_name):
                    sqlh.create_table(adb,table_name, col_names, col_types)


def boot_strapper():
    pdb = sqlh.create_db_connection(PRICES_DB_NAME, DB_TIMEOUT)
    adb = sqlh.create_db_connection(ANALYTICS_DB_NAME, DB_TIMEOUT) 

    driver_choices = []
    with open('analytics_choices.txt') as f:
        for line in f:
            driver_choices.append(tuple(line.split(':')))


    boot_strap_databases(driver_choices, pdb, adb)
    sma_mngr = ad.SMA_Manager(QUOTE_LIST, driver_choices, PRICES_DB_NAME, ANALYTICS_DB_NAME)


    adb.close()
    pdb.close()

    return sma_mngr

def update_analytics():
    pass
    

                                                    


def analytics_loop(sma_mngr):

    while(1):

        #don't need loop to update super fast
        #analytics are at a minimum performed at on minute time interavls
        time.sleep(ANALYTICS_LOOP_DELAY)
        curr_time = dt.datetime.now()

        curr_min = curr_time.minute

        if curr_min % PRICES_UPDATE_INTERVAL == 1:
            #ps.update_prices()
            #sqlh.update_row(db,PRICES_LU_TABLE,PRICES_LU_COL, int(tim.time()),1)
            update_analytics()






if __name__ == '__main__':
    sma_mngr = boot_strapper()
    analytics_loop(sma_mngr)
