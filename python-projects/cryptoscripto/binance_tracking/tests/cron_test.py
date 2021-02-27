import time


if __name__ == '__main__':

    with open('ctest.txt','a') as f:
        f.write(str(time.time()) + '\n')
