#!/usr/bin/python
# encoding: utf-8

import json
import optparse
import csv
import sys
import datetime
import influx_queries
  
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
    opt_parser.add_option('-u', '--url', dest='url', help='URL of influx', 
                          metavar='URL', default='https://calliope.pvt.spire.com/influxdb')
    opt_parser.add_option('-i', '--spire-id', dest='spire_id', help='Spire ID of filter', 
                          metavar='SPIRE_ID', default='lemur-2-chris')
    opt_parser.add_option('-s', '--start-date', dest='start_date', help='Start date of search (ex \'2015-10-01\'', 
                          metavar='START_DATE', default='2015-10-01')
    opt_parser.add_option('-e', '--end-date', dest='end_date', help='End date of search (ex \'2015-10-01\'', 
                          metavar='END_DATE', default=datetime.datetime.now().strftime('%Y-%m-%d'))   
    opt_parser.add_option('-f', '--fields', dest='fields', help='Comma delimited fields filter (ex, \'pos_x,pos_y\')',
                          metavar='FIELDS', default='')                             
    opt_parser.add_option('-v', '--verbose', dest='verbose', help='Verbose output', 
                          action='store_true', default=False)
    opt_parser.add_option('-q', '--query-type', dest='query_type', help='Query type (ex adacs, gps)', 
                          metavar='QUERY_TYPE', default='adacs')    
    opt_parser.add_option('-c', '--csv', dest='csv', help='Dump to csv', 
                          metavar='CSV', default='')
    (opt_args, args) = opt_parser.parse_args()
    
    query_types = { 
                    'gps' : (influx_queries.GPSQuery(opt_args.url, 'telemetry'), ''),
                    'adacs' : (influx_queries.ADACSQuery(opt_args.url, 'telemetry'), ''),
                }
    
    query = query_types[opt_args.query_type][0]
    res = query.search(opt_args.spire_id, opt_args.start_date, opt_args.end_date, variant=query_types[opt_args.query_type][1])
    fields = None
    if opt_args.fields:
        fields = opt_args.fields.split(',')
    res_data = influx_queries.flatten_results(json.loads(res.text), fields)
    
    if opt_args.verbose:
        print(json.dumps(res_data, indent=4, separators=(',', ':')))
        print('Length: %d' % (len(res_data) if res_data is not None else 0))
    
    if opt_args.csv != '':
        dump_csv(opt_args.csv, matches)