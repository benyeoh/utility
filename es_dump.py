#!/usr/bin/python
# encoding: utf-8

import warnings
import base64
#from urllib3.exceptions import InsecureRequestWarning
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

import json
import optparse
import csv
import sys

import es_queries

def _fetch_value(d, subfield):
    for s in subfield.split("."):
        d = d[s]
    return d

def search(name, pwd, query, limit=50):
    ES_USER = name
    ES_PASSWD = pwd
    ES_URL = 'https://{}:{}@truffula.pvt.spire.com/elasticsearch'.format(ES_USER, ES_PASSWD)
    
    es = Elasticsearch([ES_URL])
    return es.search(index="spire", body=query, size=limit, request_timeout=300, timeout=300)

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
    opt_parser.add_option('-n', '--name', dest='name', help='Login name', 
                          metavar='NAME', default='spire')
    opt_parser.add_option('-p', '--pwd', dest='pwd', help='Login password', 
                          metavar='PWD', default='')
        
    (opt_args, args) = opt_parser.parse_args()
    
    matches = search(opt_args.name, opt_args.pwd, es_queries.query_adacs_sun, limit=1000000)
    print('Array len: %d' % len(matches['hits']['hits']))

    filtered_matches = matches['hits']['hits']#filter_rows_unique(matches['hits']['hits'], es_queries.gps_unique_filter)
    #print(dir(matches))
    #print(json.dumps(filtered_matches, indent=4, separators=(',', ':')))
    dump_csv('data/jeroen_all_adacs_sun.csv', filtered_matches, es_queries.adacs_csv_filter)#, es_queries.adacs_csv_filter_desc)
    print('Total hits: %d' % matches['hits']['total'])
    #print(json.dumps(hits, indent=4, separators=(',', ':')))
