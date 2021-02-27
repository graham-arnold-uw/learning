QUOTE_LIST = ('BTC',)
PRICES_LU_TABLE = 'prices_last_update'
PRICES_DB_NAME = './price_stream/prices.db'
ANALYTICS_DB_NAME = './analytics_stream/price_analytics.db'
PRICES_LU_COL = 'last_update_time'
PRICES_UPDATE_INTERVAL = 5 # every five minutes starting at top of the hour
ANALYTICS_LOOP_DELAY = PRICES_UPDATE_INTERVAL
DB_TIMEOUT = 120
ANALYTICS_LOG_FILE = './analytics_stream/analytics.log'
ANALYTICS_CHOICES_FILE = './analytics_stream/analytics_choices.txt'
ANALYTICS_MISSED_PRICE_M = 3 * PRICES_UPDATE_INTERVAL #number of minutes permissable to deviate from expected time
ANALYTICS_MISSED_PRICE_H = 12 * PRICES_UPDATE_INTERVAL
ANALYTICS_MISSED_PRICE_D = 288 * PRICES_UPDATE_INTERVAL
