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
import gzip
    
import math
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

def plot_prn(prn, title):
    ax = plt.subplot(1, 1, 1)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator())

    cm = plt.get_cmap('gist_rainbow')    
    num_colors = len(prn.keys())
    plt.gca().set_color_cycle([cm(1.*k/num_colors) for k in range(num_colors)])

    for key, value in prn.iteritems():
        time = []
        cn0 = [] 
        for v in value:
            time.append(v['time'])
            cn0.append(v['cn0'])
        
        plt.plot(time, cn0, label='PRN %d' % (key))

    plt.legend(loc='upper right')
    plt.grid(True)
    plt.ylabel('CN0')
    plt.gcf().autofmt_xdate()
    plt.title(title)
                
    #plt.tight_layout(h_pad=-5)
    plt.show()

    
def extract_data_from_telemetry_zipped_json(filepath):
    f = gzip.open(filepath, 'r')
    json_text = f.read()
    json_data = json.loads(json_text)
    
    prn = {}
    for table_name, table in json_data.iteritems():
        for row in table['rows']:
            timestamp = row[1]
            range_data = json.loads(row[2])
            for prn_data in range_data[1:]:
                prn_slot = prn_data['prn_slot']
                prn_cn0 = prn_data['cn0']
                if prn_slot not in prn:
                    prn[prn_slot] = []
                prn[prn_slot].append({'time':datetime.datetime.utcfromtimestamp(timestamp), 'cn0':prn_cn0})
    
    return prn
        
if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--file', dest='file', help='Telemetry exported zipped json file for input', 
                          metavar='FILE', default='')
           
    (opt_args, args) = opt_parser.parse_args()
    
    data_list = []
    fm_name_list = []
    if opt_args.file != '':
        prn = extract_data_from_telemetry_zipped_json(opt_args.file)    
        plot_prn(prn, opt_args.file)
        