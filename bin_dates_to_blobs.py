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

import math
import numpy
import matplotlib.pyplot as plt

class BlobEntry:
    def __init__(self, start, end, is_sun, is_nadir):
        self.start = start
        self.end = end
        self.is_sun = is_sun
        self.is_nadir = is_nadir
            
    def jsonize(self):
        _jsonized = {
            "start" : self.start,
            "end" : self.end,
            "start_date" : str(datetime.datetime.utcfromtimestamp(self.start)),
            "end_date" : str(datetime.datetime.utcfromtimestamp(self.end)),            
            "is_sun" : self.is_sun,
            "is_nadir" : self.is_nadir
        }
        
        return _jsonized

def _fetch_value(d, subfield):
    for s in subfield.split("."):
        d = d[s]
    return d

def construct_blobs(json_data):
    blobbed_data = []
    
    threshold_start_epoch = (datetime.datetime(2015, 11, 16) - datetime.datetime(1970, 1, 1)).total_seconds()
    threshold_end_epoch = (datetime.datetime(2015, 12, 4) - datetime.datetime(1970, 1, 1)).total_seconds()
    
    for d in json_data:                        
        start_date = datetime.datetime.strptime(d["start_date"], "%Y-%m-%d %H:%M:%S")
        start_epoch = ((start_date - datetime.datetime(1970, 1, 1)).total_seconds())
        end_date = datetime.datetime.strptime(d["end_date"], "%Y-%m-%d %H:%M:%S")
        end_epoch = ((end_date - datetime.datetime(1970, 1, 1)).total_seconds())
        
        is_sun = d["is_sun"] == 'True'
        is_nadir = d["is_nadir"] == 'True'
        
        blob = BlobEntry(start_epoch, end_epoch, is_sun, is_nadir)
        if (blob.is_sun 
            and blob.is_nadir
            and blob.start >= threshold_start_epoch
            and blob.end <= threshold_end_epoch):
            print("start: %s, end: %s, is_sun: %s, is_nadir: %s" % (str(start_date), str(end_date), str(is_sun), str(is_nadir)))
            blobbed_data.append(blob)
            
    return blobbed_data

def construct_dates(json_data):
    dates_data = []
    
    for d in json_data:                        
        date = datetime.datetime.strptime(d[d.keys()[0]], "%Y-%m-%d %H:%M:%S")
        epoch = ((date - datetime.datetime(1970, 1, 1)).total_seconds())
        
        #print("date: %s, epoch: %d" % (str(date), epoch))
        dates_data.append(epoch)
            
    return dates_data    
    
if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--file', dest='file', help='CSV file input', 
                          metavar='FILE', default='')
    
    opt_parser.add_option('-d', '--dates-file', dest='dates_file', help='CSV file input for dates', 
                          metavar='DATES_FILE', default='')
    
    (opt_args, args) = opt_parser.parse_args()
    
    if opt_args.file != '':
        with open(opt_args.file, 'r') as f:
            reader = csv.DictReader(f)
            data = [r for r in reader]
            blobs = construct_blobs(data)
    
    if opt_args.dates_file != '':
        with open(opt_args.dates_file, 'r') as f:
            reader = csv.DictReader(f)
            data = [r for r in reader]
            dates = construct_dates(data)

    bin_count = []
    blob_indices = []
    cur_count = 0
    
    cur_blob_index = 0
    for epoch in dates:
        if (epoch >= blobs[cur_blob_index].start and
            epoch <= blobs[cur_blob_index].end):
            cur_count += 1
        elif epoch > blobs[cur_blob_index].end:
            while epoch > blobs[cur_blob_index].end:
                if cur_blob_index < (len(blobs)-1):
                    bin_count.append(cur_count)
                    blob_indices.append(cur_blob_index)
                    cur_blob_index += 1                    
                    cur_count = 0
                else:
                    break
            
    bin_count.append(cur_count)
              
    # Sum total time
    total_time = 0
    for index in blob_indices:
        blob = blobs[index]
        total_time += (blob.end - blob.start)
    
    # Sum total count
    total_count = 0
    for count in bin_count:
        total_count += count
        
    print("Total: %d" % len(dates))
    print("Count: %d, Time: %d secs, Average Count Per Sec: %f" % (total_count, total_time, total_count * 1.0 /float(total_time)))
    