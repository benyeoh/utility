#!/usr/bin/env python
# encoding: utf-8

import warnings
import base64

import json
import optparse
import csv
import sys
import time
import datetime

def dump_csv(filename, data, fields_desc=None):
    if sys.version_info >= (3,0,0):
        f = open(filename, 'w', newline='')
    else:
        f = open(filename, 'wb')
    
    f = csv.writer(f)
    f.writerow(data[0].keys())
    if fields_desc is not None:
        f.writerow(fields_desc)
        
    for x in data:
        f.writerow(x.values())
            
def gen_gps_times(start_date, end_date, freq=1, duration=60*60):
    gps_times = []
    start = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    start_timestamp = ((start - datetime.datetime(1970, 1, 1)).total_seconds())
    end_timestamp = ((end - datetime.datetime(1970, 1, 1)).total_seconds())
    cur_timestamp = start_timestamp
    while cur_timestamp < end_timestamp:
        for i in range(freq):
            timestamp = ((24.0 * 60.0 * 60.0) / freq) * i + cur_timestamp
            gps_times.append({ 
                                'start' : datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                                'end' : datetime.datetime.utcfromtimestamp(timestamp + duration).strftime('%Y-%m-%d %H:%M:%S'),                              
                             })        

        cur_timestamp += 60*60*24
        
    return gps_times

if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-c', '--csv', dest='csv', help='CSV file output', 
                          metavar='CSV', default='')
    opt_parser.add_option('-s', '--start', dest='start', help='Start date (ex \'2015-10-10\'', 
                          metavar='START', default='2015-10-10')
    opt_parser.add_option('-e', '--end', dest='end', help='End date (ex \'2016-01-15\'', 
                          metavar='END', default=datetime.datetime.now().strftime('%Y-%m-%d'))
    opt_parser.add_option('-f', '--freq', dest='freq', help='Frequency of time range in 24 hrs', 
                          metavar='FREQ', type='int', default=1)

    (opt_args, args) = opt_parser.parse_args()
    gps_times = gen_gps_times(opt_args.start, opt_args.end, freq=opt_args.freq)
    dump_csv(opt_args.csv, gps_times)