#!/usr/bin/python
# encoding: utf-8

import json
import optparse
import csv
import sys

import es_queries

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
    opt_parser.add_option('-n', '--name', dest='name', help='Login name', 
                          metavar='NAME', default='spire')
    opt_parser.add_option('-p', '--pwd', dest='pwd', help='Login password', 
                          metavar='PWD', default='')

    opt_parser.add_option('-v', '--verbose', dest='verbose', help='Verbose output', 
                          action='store_true', default=False)

    opt_parser.add_option('-c', '--csv', dest='csv', help='Dump to csv', 
                          metavar='CSV', default='')
    (opt_args, args) = opt_parser.parse_args()
    
    query = es_queries.ADACSQuery(opt_args.name, opt_args.pwd)
    matches = query.search_nadir_sun('lemur-2-peter', '2015-10-1', '2017-01-01', 100000000)
    matches = es_queries.flatten_results(matches)#, ['eclipse_flag', 'qbo_hat', 'omega_b'])
    
    if opt_args.verbose:
        print(json.dumps(matches, indent=4, separators=(',', ':')))
    
    if opt_args.csv != '':
        dump_csv(opt_args.csv, matches)
