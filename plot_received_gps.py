#!/usr/bin/python
# encoding: utf-8

import json
import optparse
import csv
import sys
import time
import datetime
import re

import math
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import gps_to_utc

def plot_received_gps_data(received_gps_data_list, title, y_labels=[]):
    ax = plt.subplot(111)
    plt.title('(X indicates failed to get navsol for that date, missing data indicates no beacons/tlm for that date)')   
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    
    for i, received_gps_data in enumerate(received_gps_data_list):    
        dates_success = []
        dates_failure = []
        
        for d in received_gps_data:
            date = d['gps_time']
            if d['success']:
                dates_success.append(date)
            else:
                dates_failure.append(date)
            
        plt.plot(dates_success, [i+1] * len(dates_success), 'ro', markersize=10)
        plt.plot(dates_failure, [i+1] * len(dates_failure), 'kx', markersize=10)
        #plt.setp(plt.xticks()[1], rotation=30, ha='right')
    
    plt.yticks(numpy.arange(0, len(received_gps_data_list)+2, 1.0))
    y_tick_labels = ax.get_yticks().tolist()
    y_tick_labels[0]=''
    for i, label in enumerate(y_labels):
        y_tick_labels[i+1] = label        
    y_tick_labels[-1]=''
    ax.set_yticklabels(y_tick_labels)

    #plt.tight_layout(h_pad=-1)
    plt.gcf().autofmt_xdate()
    plt.suptitle(title, size=16)
    plt.show()
    
def extract_received_gps(data):
    received_gps_data = []
    
    for d in data:                        
        dt = datetime.datetime.strptime(d['time'], "%Y-%m-%d %H:%M:%S")
        ms = float(d['sol_timestamp_ms'])
        wk = float(d['sol_timestamp_wk'])
        gps_to_utc_date = gps_to_utc.convert(wk, ms)
        received_gps_data.append( { 'time' : dt, 'gps_ms' : ms, 'gps_wk': wk, 'gps_to_utc_date' : gps_to_utc_date } )
        #print("time: %s, gps: %s" % (str(dt), str(gps_to_utc_date)))
    return received_gps_data

def extract_received_gps_from_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        data = [r for r in reader]
        received_gps_data = extract_received_gps(data)
        return received_gps_data
    return None

def _snap_to_last_gps_date(ref_datetime):
    return datetime.datetime(ref_datetime.year, ref_datetime.month, ref_datetime.day)

def process_received_gps_with_holes(received_gps):
    received_gps_with_holes = []
    for d in received_gps:
        if d['gps_wk'] == 0 and d['gps_ms'] == 0:
            missed_gps_date = _snap_to_last_gps_date(d['time'])
            if len(received_gps_with_holes) == 0:
                received_gps_with_holes.append( { 'gps_time' : missed_gps_date, 'success' : False } )
            elif missed_gps_date > received_gps_with_holes[-1]['gps_time']:
                received_gps_with_holes.append( { 'gps_time' : missed_gps_date, 'success' : False } )
        else:
            received_gps_date = _snap_to_last_gps_date(d['gps_to_utc_date'])
            if len(received_gps_with_holes) == 0:
                received_gps_with_holes.append( { 'gps_time' : received_gps_date, 'success' : True } )
            else:                
                if received_gps_with_holes[-1]['gps_time'] < received_gps_date:
                    received_gps_with_holes.append( { 'gps_time' : received_gps_date, 'success' : True } )
                elif received_gps_with_holes[-1]['gps_time'] == received_gps_date:
                    received_gps_with_holes[-1]['success'] = True
                    
                next_gps_timedelta = datetime.timedelta(hours=24)
                end_date = _snap_to_last_gps_date(d['time'])
                cur_date = _snap_to_last_gps_date(received_gps_with_holes[-1]['gps_time'] + next_gps_timedelta)
                while cur_date <= end_date:
                    received_gps_with_holes.append( { 'gps_time' : cur_date, 'success' : False } )
                    cur_date = _snap_to_last_gps_date(received_gps_with_holes[-1]['gps_time'] + next_gps_timedelta)

    return received_gps_with_holes

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
        
if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--files', dest='file', help='CSV files input', 
                          metavar='FILE', default='')
    #opt_parser.add_option('-c', '--csv', dest='csv', help='CSV file for output of plot stats', 
    #                      metavar='OVERLAY', default='')
       
    (opt_args, args) = opt_parser.parse_args()
    
    received_gps_data_list = []
    fm_name_list = []
    if opt_args.file != '':
        filenames = opt_args.file.split(',')
        for file in filenames:
            fm_str = file.split('/')[-1].split('_')[0].upper()

            fm_name_list.append(fm_str)
            received_gps_data = extract_received_gps_from_csv(file)
            received_gps_data_with_holes = process_received_gps_with_holes(received_gps_data)
            received_gps_data_list.append(received_gps_data_with_holes)
            
        plot_received_gps_data(received_gps_data_list, 'GPS Nav Sol Received', fm_name_list)
        