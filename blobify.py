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

class BlobEntry:
    def __init__(self, start, is_sun, is_nadir):
        self.start = start
        self.end = start
        self.is_sun = is_sun
        self.is_nadir = is_nadir
    
    def grow_range(self, new_end):
        #print("new_end: %d, old_end: %d" % (new_end, self.end))
        assert(self.end <= new_end)
        self.end = new_end
        
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

def dump_csv(filename, data, fields, fields_desc=None):
    if sys.version_info >= (3,0,0):
        f = open(filename, 'w', newline='')
    else:
        f = open(filename, 'wb')
    
    f = csv.writer(f)
    f.writerow(fields)
    if fields_desc is not None:
        f.writerow(fields_desc)
        
    for x in data:
        f.writerow([_fetch_value(x, field) for field in fields])
            
def blobify_adacs_beacons(data):
    blobbed_data = []
    cur_blob_entry = BlobEntry(0, False, False)
    
    THRESHOLD = 60 * 60 * 4
    
    for d in data:                        
        dt = datetime.datetime.strptime(d["_source.meta.time"], "%Y-%m-%dT%H:%M:%S")
        epoch_timestamp = ((dt-datetime.datetime(1970, 1, 1)).total_seconds())
        is_sun = int(d["_source.response.eclipse_flag"]) == 0
        is_nadir = d["_source.response.acs_op_mode_str"] == 'NORMAL'
        if (epoch_timestamp - cur_blob_entry.end) < THRESHOLD and \
           (is_sun == cur_blob_entry.is_sun) and \
           (is_nadir == cur_blob_entry.is_nadir):
            # Grow range
           cur_blob_entry.grow_range(epoch_timestamp)
        else:
            if cur_blob_entry.is_sun:
                blobbed_data.append(cur_blob_entry.jsonize())
            cur_blob_entry = BlobEntry(epoch_timestamp, is_sun, is_nadir)
            
    for b in blobbed_data:
        print(b)
        #print("From %s, To %s\n" % (datetime.datetime.utcfromtimestamp(b["start"]), datetime.datetime.utcfromtimestamp(b["end"])))

    dump_csv("blobify.csv", blobbed_data, ["start_date", "end_date", "is_sun", "is_nadir"])

if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--file', dest='file', help='CSV file input', 
                          metavar='FILE', default='')
        
    (opt_args, args) = opt_parser.parse_args()
    
    if opt_args.file != '':
        with open(opt_args.file, 'r') as f:
            reader = csv.DictReader(f)
            data = [r for r in reader][1:]
            blobify_adacs_beacons(data)
            