from collections import deque

class SMA:



    def __init__(self, data_rate, data_rate_type, sma_rate, sma_rate_type):

        if data_rate_type == 'm':
            if sma_rate_type == 'm':
                factor = 1
            elif sma_rate_type == 'h':
                factor = 60
            elif sma_rate_type == 'd':
                factor = 1440

        sma_rate_scaled = factor * sma_rate

        self.q_size = int(sma_rate_scaled / data_rate)

        self.data_q = deque(maxlen = self.q_size)

        self.avg = float('NaN')


    def update(self, val):
        if len(self.data_q) < self.q_size - 1:
            self.data_q.append(val)
            return sum(self.data_q) / len(self.data_q)

        if len(self.data_q) == self.q_size - 1:
            self.data_q.append(val)
            self.avg = sum(self.data_q) / self.q_size
            return self.avg


        old_head = self.data_q[0]
        self.data_q.append(val)
        self.avg -= old_head / self.q_size
        self.avg += val / self.q_size
        return self.avg


    def get_sma(self):

        if len(self.data_q)< self.q_size:
            return float('NaN')

        self.avg = sum(self.data_q) / self.q_size

        return self.avg
