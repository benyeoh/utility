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

def plot_roll_data(roll_data, title, overlay_data=None, is_mod_24_hrs=False):
    # Get dates modulo 24 hrs
    time_stamps = []
    roll_x = []
    roll_y = []
    roll_z = []
    dates = []
    
    for d in roll_data:
        if is_mod_24_hrs:
            time_stamps.append((d['time'].hour * 60 * 60 + d['time'].minute * 60 + d['time'].second) / 3600.0)
        dates.append(d['time'])
        roll = d['roll']
        roll_x.append(roll[0])
        roll_y.append(roll[1])
        roll_z.append(roll[2])
        
    ax = plt.subplot(311)
    plt.title('Roll X')
    plt.ylabel('Degrees per sec')
    if is_mod_24_hrs:
        plt.plot(time_stamps, roll_x, 'ro')
        plt.xlabel('Time in 24 Hr Period')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, roll_x, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        plt.xlabel('No. of days since start date')
        plt.gcf().autofmt_xdate()
        #plt.setp(plt.xticks()[1], rotation=30, ha='right')
    
    ax = plt.subplot(312)
    plt.title('Roll Y')
    plt.ylabel('Degrees per sec')
    if is_mod_24_hrs:
        plt.plot(time_stamps, roll_y, 'ro')
        plt.xlabel('Time in 24 Hr Period')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, roll_y, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        #plt.xlabel('No. of days since start date')
        plt.gcf().autofmt_xdate()
        #plt.setp(plt.xticks()[1], rotation=30, ha='right')
        
    ax = plt.subplot(313)
    plt.title('Roll Z')
    plt.ylabel('Degrees per sec')
    if is_mod_24_hrs:
        plt.plot(time_stamps, roll_z, 'ro')
        plt.xlabel('Time in 24 Hr Period')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, roll_z, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        #plt.setp(plt.xticks()[1], rotation=30, ha='right')
        plt.gcf().autofmt_xdate()
        #plt.xlabel('No. of days since start date')
    
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
        
    #for d in roll_data:
    #    print("Date: %s, Roll: [%f, %f, %f]" % (d['time'], d['roll'][0], d['roll'][1], d['roll'][2]))        
    return roll_data

def extract_roll_from_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        data = [r for r in reader]
        roll_data = extract_roll(data)
        return roll_data
    return None

def extract_overlay_times(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        data = [r for r in reader]
        overlay_times_data = [ 
                              {
                                'start' : datetime.datetime.strptime(d['start'], "%Y-%m-%d %H:%M:%S"),
                                'end' : datetime.datetime.strptime(d['end'], "%Y-%m-%d %H:%M:%S") 
                               } for d in data 
                             ]        
        return overlay_times_data
    return None

def _sum_roll_stats_in_range(start_datetime, end_datetime, roll_data):
    start_timestamp = ((start_datetime - datetime.datetime(1970, 1, 1)).total_seconds())
    end_timestamp = ((end_datetime - datetime.datetime(1970, 1, 1)).total_seconds())
    sum = [0.0, 0.0, 0.0]
    sum_sq = [0.0, 0.0, 0.0]
    num_sum = 0.0
    for data in roll_data:
        timestamp = ((data['time'] - datetime.datetime(1970, 1, 1)).total_seconds())
        if timestamp >= start_timestamp and timestamp <= end_timestamp:
            sum[0] += data['roll'][0]
            sum[1] += data['roll'][1]
            sum[2] += data['roll'][2]
            sum_sq[0] += (data['roll'][0] ** 2.0)
            sum_sq[1] += (data['roll'][1] ** 2.0)
            sum_sq[2] += (data['roll'][2] ** 2.0)
            num_sum += 1
    
    return (sum, sum_sq, num_sum)

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
        
def compute_roll_stats_in_ranges(start_end_ranges, roll_data):
    total_sum = [0.0, 0.0, 0.0]
    total_sum_sq = [0.0, 0.0, 0.0]
    total_num_sum = 0.0
    
    for range in start_end_ranges:
        (sum, sum_sq, num_sum) = _sum_roll_stats_in_range(range['start'], range['end'], roll_data)
        total_sum[0] += sum[0]
        total_sum[1] += sum[1]
        total_sum[2] += sum[2]
        total_sum_sq[0] += sum_sq[0]
        total_sum_sq[1] += sum_sq[1]
        total_sum_sq[2] += sum_sq[2]
        total_num_sum += num_sum

    if total_num_sum > 0:
        mean = [total_sum[0] / total_num_sum, total_sum[1] / total_num_sum, total_sum[2] / total_num_sum]
        std_dev = [math.sqrt(total_sum_sq[0] / total_num_sum), math.sqrt(total_sum_sq[1] / total_num_sum), math.sqrt(total_sum_sq[2] / total_num_sum)]
        return { 'mean' : mean, 'std_dev' : std_dev }
    return {}

if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--file', dest='file', help='CSV file input', 
                          metavar='FILE', default='')
    opt_parser.add_option('-o', '--overlay', dest='overlay', help='CSV file for overlay input', 
                          metavar='OVERLAY', default='')
    opt_parser.add_option('-c', '--csv', dest='csv', help='CSV file for output of plot stats', 
                          metavar='OVERLAY', default='')
       
    (opt_args, args) = opt_parser.parse_args()
    
    if opt_args.file != '':
        fm_str = opt_args.file.split('/')[-1].split('_')[0].upper()
        
        roll_data = extract_roll_from_csv(opt_args.file)
        start_date_str = roll_data[0]['time'].strftime('%Y-%m-%d')
        end_date_str = roll_data[-1]['time'].strftime('%Y-%m-%d')

        overlay_times = None
        total_roll_stats = []
        if opt_args.overlay != '':
            overlay_times = extract_overlay_times(opt_args.overlay)
            roll_stats = compute_roll_stats_in_ranges(overlay_times, roll_data)
            roll_stats['_name'] = 'overlay_stats'
            total_roll_stats.append(roll_stats)
            
        roll_stats = compute_roll_stats_in_ranges([{'start' : roll_data[0]['time'], 'end' : roll_data[-1]['time']}], roll_data)
        roll_stats['_name'] = 'total_stats'
        total_roll_stats.append(roll_stats)
        print(json.dumps(total_roll_stats, indent=4, separators=(',', ':'), sort_keys=True))
        if opt_args.csv != '':
            dump_csv(opt_args.csv, total_roll_stats)
        plot_roll_data(roll_data, '%s Roll 24 Hr Plot (From %s to %s)' % (fm_str, start_date_str, end_date_str), overlay_data=overlay_times)
        