#!/usr/bin/python
# encoding: utf-8

import warnings
import base64

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

def plot_roll_data(roll_data, title):
    # Get dates modulo 24 hrs
    time_stamps = []
    roll_x = []
    roll_y = []
    roll_z = []
    dates = []
    
    for d in roll_data:
        #time_stamps.append((d['time'].hour * 60 * 60 + d['time'].minute * 60 + d['time'].second) / 3600.0)
        time_stamps.append((d['time']-roll_data[0]['time'].replace(second=0, microsecond=0)).total_seconds() / 86400.0)
        dates.append(d['time'])
        roll = d['roll']
        roll_x.append(roll[0])
        roll_y.append(roll[1])
        roll_z.append(roll[2])
        
    ax = plt.subplot(311)
    plt.title('Roll X')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.plot(dates, roll_x, 'ro')
    plt.xlabel('No. of days since start date')
    plt.ylabel('Degrees per sec')
    plt.gcf().autofmt_xdate()
    #plt.setp(plt.xticks()[1], rotation=30, ha='right')
    
    ax = plt.subplot(312)
    plt.title('Roll Y')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.plot(dates, roll_y, 'ro')
    #plt.xlabel('No. of days since start date')
    plt.ylabel('Degrees per sec')
    plt.gcf().autofmt_xdate()
    #plt.setp(plt.xticks()[1], rotation=30, ha='right')
    
    ax = plt.subplot(313)
    plt.title('Roll Z')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.plot(dates, roll_z, 'ro')
    #plt.setp(plt.xticks()[1], rotation=30, ha='right')
    plt.gcf().autofmt_xdate()
    #plt.xlabel('No. of days since start date')
    plt.ylabel('Degrees per sec')
    
    plt.tight_layout(h_pad=-1)
    plt.suptitle(title, size=16)
    plt.show()
    
def extract_roll(data):
    roll_data = []
    
    for d in data:                        
        dt = datetime.datetime.strptime(d['time'], "%Y-%m-%d %H:%M:%S")
        #epoch_timestamp = ((dt-datetime.datetime(1970, 1, 1)).total_seconds())
        # Remove crap from qbo_hat_str
        if d['omega_b'] is not None and d['omega_b'] != '':
            roll_str = re.sub('[\[\]]', '', d['omega_b']).split(',')
            roll_val = [float(val.strip()) for val in roll_str]
        else:
            roll_val = [float(d['omega_b_0']), float(d['omega_b_1']), float(d['omega_b_2'])]
            
        #if d["_source.response.acs_op_mode_str"] != 'NOOP':
        roll_data.append( { 'time' : dt, 'roll' : roll_val } )
        
    for d in roll_data:
        print("Date: %s, Roll: [%f, %f, %f]" % (d['time'], d['roll'][0], d['roll'][1], d['roll'][2]))        
    return roll_data

if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--file', dest='file', help='CSV file input', 
                          metavar='FILE', default='')
        
    (opt_args, args) = opt_parser.parse_args()
    
    if opt_args.file != '':
        fm_str = opt_args.file.split('/')[-1].split('_')[0].upper()
        
        with open(opt_args.file, 'r') as f:
            reader = csv.DictReader(f)
            data = [r for r in reader]
            roll_data = extract_roll(data)
            start_date_str = roll_data[0]['time'].strftime('%Y-%m-%d')
            end_date_str = roll_data[-1]['time'].strftime('%Y-%m-%d')
            plot_roll_data(roll_data, '%s Roll 24 Hr Plot (From %s to %s)' % (fm_str, start_date_str, end_date_str))
            