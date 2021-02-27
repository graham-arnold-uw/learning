
import price_stream.trading_pairs as tp




if __name__ == '__main__':

    sym_pairs = tp.poll_pairs('BTC')
    print(sym_pairs)
