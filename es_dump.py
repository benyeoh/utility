#!/usr/bin/python
# encoding: utf-8

import warnings
import base64
#from urllib3.exceptions import InsecureRequestWarning
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import optparse

# Handle option parsing
opt_parser = optparse.OptionParser()
opt_parser.add_option('-n', '--name', dest='name', help='Login name', 
                      metavar='NAME', default='spire')
opt_parser.add_option('-p', '--pwd', dest='pwd', help='Login password', 
                      metavar='PWD', default='')

(opt_args, args) = opt_parser.parse_args()

ES_USER = opt_args.name
ES_PASSWD = opt_args.pwd
ES_URL = 'https://{}:{}@truffula.pvt.spire.com/elasticsearch'.format(ES_USER, ES_PASSWD)

es = Elasticsearch([ES_URL])
print(es)

#es.get(index="spire", doc_type="gps*", id=1)
s = es.search(index="spire", q='_type:gps*')
print(s)
