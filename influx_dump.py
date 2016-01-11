#!/usr/bin/python
# encoding: utf-8

import warnings
import base64

import requests

import json
import optparse
import csv
import sys

def _fetch_value(d, subfield):
    for s in subfield.split("."):
        d = d[s]
    return d

def _get_response(url, db, query):
    search_data = { 'q' : query, 'db' : db }
    init_url = '/'.join([url, 'query?pretty=true'])
    res = requests.get('&'.join([init_url, 'db=%s' % db, 'q=%s' % query]))
    print(res.url)
    return json.loads(res.text)

def search(url, db, table, fields, spire_id, start, end):
    query = 'SELECT %s FROM /%s.*/ '\
            'WHERE spire_id=\'%s\'' \
            'AND time >= \'%s\' ' \
            'AND time <= \'%s\' ' \
            'ORDER BY time ASC'
    query = query % (','.join(fields), table, spire_id, start, end)
    return _get_response(url, db, query)
    
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

def filter_rows_unique(data, unique_fields):
    filtered = []
    uniques = {}
    for x in data:
        check_unique = tuple([_fetch_value(x, field) for field in unique_fields])
        if check_unique not in uniques:
            uniques[check_unique] = True
            filtered.append(x)
    
    return filtered
        
if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-u', '--url', dest='url', help='URL of influx', 
                          metavar='URL', default='https://calliope.pvt.spire.com/influxdb')
    opt_parser.add_option('-i', '--spire-id', dest='spire_id', help='Spire ID of filter', 
                          metavar='SPIRE_ID', default='lemur-2-chris')
    opt_parser.add_option('-n', '--name', dest='name', help='Login name', 
                          metavar='NAME', default='spire')
    opt_parser.add_option('-p', '--pwd', dest='pwd', help='Login password', 
                          metavar='PWD', default='')
        
    (opt_args, args) = opt_parser.parse_args()
        
    res = search(opt_args.url, 'telemetry', 'gps_pos_vel', ['pos_x', 'pos_y'], opt_args.spire_id, '2015-10-15', '2015-12-10')
    
    print(json.dumps(res['results'][0]['series'][0]['values'], indent=4, separators=(',', ':')))
