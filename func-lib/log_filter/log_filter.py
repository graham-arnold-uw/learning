#!/usr/bin/env python3

import sys, glob, getopt
from datetime import date

#log file name tempalte
# E94940_2021_04_22_115739


def filter_mf4(dir):
    files = [f.split('/')[-1] for f in glob.glob(dir+"*.MF4")]
    return files

#process user date input into datetime object
def process_date(date_in):
    mon,day,year = date_in.split('/')
    date_out = date(year=int(year), month=int(mon), day=int(day))
    return date_out

def build_filter(mode):

    if mode == 'range':
        def filter_func_range(all_files, params):
            str_date,end_date = params
            filtered = []
            #print(all_files)
            for file in all_files:
                chunks = file.split('_')
                truck,year,mon,day,time = chunks
                file_date = date(year=int(year), month=int(mon), day=int(day))
                #print(file_date)
                if file_date >= str_date and file_date <= end_date:
                    filtered.append(file)
                    #print('hit')
            return filtered
        return filter_func_range
    return None






def driver():
    num_args = len(sys.argv)
    args = sys.argv
    #print(args[0])
    #target_directory = args[1]
    #output_file = args[2]
    #print(target_directory)
    #print(output_file)

    opts, args_left = getopt.getopt(args[1:], '', ['mode=','range-start=', 'range-end='])
    target_directory = args_left[0]
    output_file = args_left[1]
    all_MF4 = filter_mf4(target_directory)
    #print(all_MF4)
    #print(args_left)

    curr_mode = 'range'
    for opt,arg in opts:
        if opt == "--mode":
            curr_mode = arg


    if curr_mode == 'range':
        r_str = None
        r_end = None
        for opt,arg in opts:
            if opt == '--range-start':
                r_str = arg
            elif opt == '--range-end':
                r_end = arg

        if r_str == None:
            raise ValueError('range-start command line argument value not provided despite range lookup mode selected')

        if r_end == None:
            raise ValueError('range-end command line argument value not provided despite range lookup mode selected')


        r_str_dt = process_date(r_str)
        r_end_dt = process_date(r_end)
        params = (r_str_dt, r_end_dt)

        filter_func = build_filter(curr_mode)
        filtered_MF4 = filter_func(all_MF4,params)
        #print(filtered_MF4)

    #print(all_MF4)

    with open(output_file, 'x') as fout:
        files_out = [curr_file + '\n' for curr_file in filtered_MF4]
        fout.writelines(files_out)






if __name__ == '__main__':
    driver()
