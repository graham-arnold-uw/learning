#Author: Graham Arnold
#Date created: 8/18/20
#Last update: -
#
#This file defines helper classes and functions for dealing with the binance api


class BinanceException(Exception):
    def __init__(self, status_code):

        self.status_code = status_code
    
        message = f"{status_code}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)
