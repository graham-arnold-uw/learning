def find_added_columns(new_set,prev_set):
    res = set()
    for new in new_set:
        if new not in prev_set:
            res.add(new)
    return res

def find_deleted_columns(new_set, prev_set):
    res = set()
    for prev in prev_set:
        if prev not in new_set:
            res.add(prev)
    return res

#inputs
#   quote: quote currency
#   timescale: timescale (M, H, D)
#   slots: how many slots for SMA (3,4,30)
#
#output
#   table_name: BTC_SMA_30M
def get_sma_table_name(quote, timescale, slots):
    return str(quote) + '_SMA_' + str(slots) + str(timescale)


def construct_analytics_tablename(quote, antype, timescale, slots):
    return str(quote) + '_' + str(antype) + '_' + str(slots) + str(timescale)

def construct_prices_tablename(quote):
    return str(quote)+ '_prices'



     
