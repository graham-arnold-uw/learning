#!/usr/bin/python

import sys


pw = 'abc'
test1 = '6eu5ckiq7wof5eh7'
test2 = 'GBDUSMSMHA2DATKM'

def driver():
    args = sys.argv
    num_args = len(args)

    infile, outfile, pw, dir = args

    shift_func = caesar_factory(dir)



def caeser_factor(dir):


    def shifter(indata, pw):
        pwlen = len(pw)
        inlen  = len(indata)
        outdata = []

        ptr_in = 0
        ptr_pw = 0

        while ptr_in < inlen:
            char_in = indata[ptr_in]
            char_pw = pw[ptr_pw]
            if dir == 'encrypt':
                out_char = ord(char_in) + ord(char_pw) % 256
            elif dir == 'decrypt':
                out_char = ord(char_in) - ord(char_pw) % 256
            else:
                raise IllegalArgumentException("invalid argument for shift mode, enter either 'encrypt' or 'decrypt'")
            outdata.append(out_char)
            ptr_in += 1
            ptr_pw += 1
            if ptr_pw >= pwlen:
                ptr_pw = 0

        res = "".join(outdata)
        return res









if __name__ == '__main__':
    driver()
