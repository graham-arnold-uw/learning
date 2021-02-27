DB_NAME = './price_stream/prices.db'
PRICE_STREAM_LOG = './price_stream/price_stream.log'
DB_TIMEOUT = 120
SYMBOL_TABLE_NAME = 'symbols'
SYMBOL_TABLE_LU_NAME = 'symbols_last_update'
PRICES_TABLE_NAME = 'prices'
COL_LIST = ('BTC',)
QUOTE_LIST = ('BTC',)
COL_TYPES = ('text',)
TIME_COL = 'symbols'
TIME_COL_TYPES = 'text'
TIME_TABLE_NAME = 'last_update'
SECONDS_PER_DAY = 84600
REQUESTS_LIM = 0.075 #1 per 0.075 sec


PRICES_UPDATE_INTERVAL = 5
