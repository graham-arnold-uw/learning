from collections import deque
import time
from collections import defaultdict
from analytics_stream.analytics_engine_params import *
import utilities.sql_helpers as sqlh




def sma_driver(row_matrix):
    m = len(row_matrix)
    n = len(row_matrix[0])

    if m == 0 or n == 0:
        raise ValueError

    res = [0 for i in range(n)]

    for i in range(m):
        for j in range(n):
            if row_matrix[i][j] != None and res[j] != None:
                res[j] += row_matrix[i][j]
            else:
                res[j] = None

    res = [round(el / m,20) if el != None else None for el in res]
    return res


def ema_driver(row_matrix):
    pass





class SMA:



    def __init__(self, length):
        self.q_size = length

        self.data_q = deque(maxlen = self.q_size)

        self.avg = float('NaN')

        self.missed_updates = 0


    def update(self, val):
        #self.missed_updates = 0
        if len(self.data_q) < self.q_size:
            self.data_q.append(val)
            self.avg = sum(self.data_q) / len(self.data_q)
            return self.avg


        old_head = self.data_q[0]
        self.data_q.append(val)
        self.avg -= old_head / self.q_size
        self.avg += val / self.q_size
        return self.avg


    def get_sma(self):

        if len(self.data_q) == 0:
            return float('NaN')

        self.avg = sum(self.data_q) / self.q_size

        return self.avg


#SMA Manager will be used to hold the requested SMA queues in memory as the analysis engine runs
#the manager will also have to keep track of what time each queue accepts a new value
#every time a new price is available the analysis engine will attempt to post a new price to the SMA manager
#the SMA manager will update the necessary Q's or none at all
#
#The SMA manager must operate independent of the price stream SW. Therefore if the price stream stops
#and the price data is stale, the analysis engine will notify the SMA manager and the SMA manager.
#if the data is stale and one of the queue's requires a new value the SMA manager will update the
#Queue with the last valid value seen and increment the missed value counter
#if too many missed values the queue shall be dumped and reset
#
#SMA manager should also initialize the qeueus from the most recent set of contiguous historical data

class SMA_Manager:



    def __init__(self, quote_list, driver_choices, prices_db_name, analytics_db_name):


        self.quote_list = quote_list
        self.driver_choices = dict(driver_choices)

        for k in driver_choices.keys():
            choices = self.driver_choices[k]
            if len(choices) == 0:
                self.driver_choices[k] = None
            else:
                choices = choices.split(',')
                self.driver_choices[k] = choices

        self.prices_db_name = prices_db_name
        self.analytics_db_name = analytics_db_name

        pdb = sqlh.create_db_connection(self.prices_db_name, DB_TIMEOUT)
        #self.bq_pairs = self.get_bq_pairs(pdb)

        self.q_tree = {}

        self.initialize_q_tree()


        self.initialize_queues(pdb)


        pdb.close()

    #creates a dict data struct to hold mapping of quote -> [list of currency pairs]
    def get_bq_pairs(self, pdb):
        res = defaultdict(list)
        for quote in self.quote_list:
            price_table_name = quote + '_prices'
            price_table_name = quote
            price_cols = sqlh.get_column_names(pdb, price_table_name)
            curr_pairs = [col[0] for col in price_cols]
            res[quote] = curr_pairs

        return res



    #construct the data structures needed to manages all the requested analysis
    #Created in a dictionary heirarchy as follows:
    # quote currency - > base currnecy pair 0- > dict of interval type -> deques of interval selections
    # For example:
    #{'BTC' : {'M': [[30Q],[45Q]], 'H':[[4Q],[6Q]], 'D':None}, 'ETH : ...etc}
    #
    #Note: minute queue length is scaled by the price update rate
    # (ie 5minutes update rate = 6 slot Q for 30 min SMA)
    def initialize_q_tree(self):
        for quote in self.quote_list:
            choices_dict = {}
            for k in self.driver_choices.keys():
                if k == 'M':
                    factor = 1 / PRICES_UPDATE_INTERVAL
                else:
                    factor = 1
                choices = self.driver_choices[k]
                if choices != '':
                    q_collec = []
                    for c in choices:
                        cnum = int(c)
                        qlen = int(factor * cnum)
                        q = deque(maxlen=qlen)
                        q_collec.append(q)
                    choices_dict[k] = q_collec
                else:
                    choices_dict[k] = None
            self.q_tree[quote] = choices_dict




    #check current time
    #for each quote
    #starting from most recently posted price
    #get contiguous block of valid prices up to len of current SMA queue
    #fill SMA queue
    def initialize_queues(self, pdb):

        for quote in self.q_tree:
            choices_dict = self.q_tree[quote]

            for choice in choices_dict:
                if choices_dict[choice]:
                    q_list = choices_dict[choice]

                    for q in q_list:
                        self.init_q_fill(choice, q, pdb, quote)


    #take a queue, an interval choice and a database connection
    #fill queue as much as possible from the most recently available price db entries
    def init_q_fill(self,choice,q,pdb,quote):
        q_maxlen = q.maxlen
        price_table_name = quote + '_prices'
        pdb_len = sqlh.count_rows(pdb, price_table_name)

        if pdb_len == 0:
            return

        if choice == 'M':
            gap = 1
        elif choice == 'H':
            gap = 60 // PRICES_UPDATE_INTERVAL
        elif choice == 'D':
            gap = 1440 // PRICES_UPDATE_INTERVAL
        else:
            raise ValueError

        num_entries_needed = q_maxlen * gap + 1

        if pdb_len < num_entries_needed:
            if pdb_len % gap == 0:
                tar_itrs = pdb_len / gap
            else:
                tar_itrs = (pdb_len // gap) + 1
        else:
            tar_itrs = q_maxlen


        curr_rowid = pdb_len

        for i in range(tar_itrs):
            q.appendleft(curr_rowid)
            curr_rowid -= gap




    #don't forget in the main post price operation to include
    #provisions to popuplate the rest of the row ID pointers if
    # a queue does not contain all the pointers after initialization
    #so check if q is less than maxlen and if so need to check if we
    #have enough values in the DB to add another rowid pointer
    def post_price(self):
        pass
