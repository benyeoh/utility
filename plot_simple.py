#!/usr/bin/python
# encoding: utf-8

import json
import optparse
import csv
import sys
import time
import datetime
import re
import random

import math
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cmx
import matplotlib.colors as colors

def get_cmap(N):
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct 
    RGB color.'''
    color_norm  = colors.Normalize(vmin=0, vmax=N-1)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv') 
    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color

def plot_simple_data(data_list, title, data_labels=[]):
    keys = data_list[0][0].keys()
    
    cmap = get_cmap(len(data_list))
    
    for i, key in enumerate(keys):
        if key != 'time':
            if type(data_list[0][0][key]) is not str:           
                ax = plt.subplot(len(keys)-1, 1, i+1)
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
                plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
                cm = plt.get_cmap('gist_rainbow')
                
                num_colors = len(data_list)
                plt.gca().set_color_cycle([cm(1.*k/num_colors) for k in range(num_colors)])

                for j, data in enumerate(data_list):    
                    dates = []
                    values = []        
                    for d in data:
                        date = d['time']
                        dates.append(date)
                        values.append(d[key])
                                            
                    plt.plot(dates, values, label=data_labels[j])
        
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.ylabel(key)
                plt.gcf().autofmt_xdate()
                plt.suptitle(title, size=16)
                
    #plt.tight_layout(h_pad=-5)
    plt.show()
    
def extract_data(data):
    extracted_data = []
    
    for d in data:
        new_data = {}
        for key in d.iterkeys():
            if key == 'time':
                dt = datetime.datetime.strptime(d['time'], "%Y-%m-%d %H:%M:%S")
                new_data['time'] = dt
            else:
                try:
                    new_data[key] = float(d[key])
                except ValueError:
                    new_data[key] = d[key]
            
        extracted_data.append(new_data)
        #print("time: %s, gps: %s" % (str(dt), str(gps_to_utc_date)))
    return extracted_data

def extract_data_from_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f, dialect="excel")
        data = [r for r in reader]
        extracted_data = extract_data(data)
        return extracted_data
    return None

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
    
    data_list = []
    fm_name_list = []
    if opt_args.file != '':
        filenames = opt_args.file.split(',')
        for file in filenames:
            fm_str = file.split('/')[-1].split('_')[0].upper()

            fm_name_list.append(fm_str)
            data = extract_data_from_csv(file)
            data_list.append(data)
            
        plot_simple_data(data_list, '', fm_name_list)
        