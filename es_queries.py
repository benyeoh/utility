#!/usr/bin/python
# encoding: utf-8

from elasticsearch import Elasticsearch

import json
import datetime
'''
search_query3 = {
                   "query" : {
                       "query_string" : {
                            "fields" :["_type"],
                            "query" : "pdu*",
                        },
                   },
                }

search_query9 = {
                   "query" : {
                       "filtered" : {
                           "query" : {
                                "term" : {
                                    #"fields" :["meta.spire_id"],
                                    "meta.spire_id" : "lemur-2-joel"
                                }
                            },
    
                            "filter": [ {
                                "bool" : {
                                    "must" : [{ "term" : { "_type" : "gps_status" } }]
                                }},
                                
                                {       
                                "range" : {
                                    "meta.time" : {
                                        "gte" : "2015-11-30",
                                        "format": "yyyy-MM-dd"                                        
                                    },
                                }}
                            ],
                        },
                    },
                }

search_query10 = {
                   "query" : {
                       "filtered" : {
                           "query" : {
                                "query_string" : {
                                    "fields" :["_type"],
                                    "query" : "gps*",
                                }
                            },
    
                            "filter": [ {
                                "bool" : {
                                    "must" : [{ "term" : { "meta.time" : "2015-11-25T09:11:49" } }]
                                }},
                            ],
                        },
                    },
                }
'''

class ESQuery:
    def __init__(self, name, pwd):
        ES_URL = 'https://{}:{}@truffula.pvt.spire.com/elasticsearch'.format(name, pwd)    
        self.es = Elasticsearch([ES_URL])
        self.query = {}
        
    def _add_to_filters(self, key, value, filters):
        if filters.has_key(key):
            filters[key].extend(value)
        else:
            filters[key] = value
        
    def _make_query(self, filters):
        _query = {
           "query" : {
               "filtered" : {    
                    "filter": {
                        "bool" : {
                        }
                    }              
                }
            },
            
            "sort": [
                { "meta.time" : { "order": "asc" } },
            ] 
        }
        
        for key, value in filters.iteritems():
            _query["query"]["filtered"]["filter"]["bool"][key] = value
        
        self.query = _query

    def _filter_default(self, spire_id, from_date, to_date, filters):
        _must = [
                    { "term" : { "meta.spire_id.raw" : "%s" % spire_id } },
                    { "range" : { "meta.time" : { "gte" : "%s" % from_date, "format": "yyyy-MM-dd" } } },
                    { "range" : { "meta.time" : { "lte" : "%s" % to_date, "format": "yyyy-MM-dd" } } }
                ]
        
        self._add_to_filters("must", _must, filters)            
        
    def _search(self, size_limit):
        return self.es.search(index="spire", body=self.query, size=size_limit, request_timeout=300, timeout=300)

    def _search_default(self, spire_id, from_date, to_date, filters, size_limit=10000000):
        self._filter_default(spire_id, from_date, to_date, filters)
        self._make_query(filters)
        return self._search(size_limit)
    
class GPSQuery(ESQuery):
    def __init__(self, name, pwd):
        ESQuery.__init__(self, name, pwd)

    def _filter_type(self, filters):
        _must = [ { "term" : { "_type" : "gps_status" } } ]
        self._add_to_filters("must", _must, filters)

    def _filter_valid(self, filters):
        _must_not = [ { "term" : { "response.pos_x" : 0.0 } } ]
        self._add_to_filters("must_not", _must_not, filters)
        self._filter_gps(filters)
        
    def search(self, spire_id, from_date, to_date, size_limit):
        filters = {}
        self._filter_gps(filters)
        return self._search_default(spire_id, from_date, to_date, filters, size_limit)

    def search_valid(self, spire_id, from_date, to_date, size_limit):
        filters = {}
        self._filter_type(filters)
        self._filter_valid(filters)
        return self._search_default(spire_id, from_date, to_date, filters, size_limit)

class ADACSQuery(ESQuery):
    def __init__(self, name, pwd):
        ESQuery.__init__(self, name, pwd)

    def _filter_type(self, filters):
        _must = [ { "term" : { "_type" : "adacs_status_std" } } ]
        self._add_to_filters("must", _must, filters)

    def _filter_sun(self, filters):
        _must = [ { "term" : { "response.eclipse_flag" : 0 } } ]
        self._add_to_filters("must", _must, filters)

    def _filter_acquisition(self, filters):
        _must = [ { "term" : { "response.acs_op_mode_str.raw" : "ACQUISITION" } } ]
        self._add_to_filters("must", _must, filters)

    def _filter_nadir(self, filters):
        _must = [ { "term" : { "response.acs_op_mode_str.raw" : "NORMAL" } } ]
        self._add_to_filters("must", _must, filters)
    
    def search(self, spire_id, from_date, to_date, size_limit):
        filters = {}
        self._filter_type(filters)
        return self._search_default(spire_id, from_date, to_date, filters, size_limit)

    def search_nadir_sun(self, spire_id, from_date, to_date, size_limit):
        filters = {}
        self._filter_type(filters)
        self._filter_sun(filters)
        self._filter_nadir(filters)
        return self._search_default(spire_id, from_date, to_date, filters)

    def search_acquisition_sun(self, spire_id, from_date, to_date, size_limit):
        filters = {}
        self._filter_type(filters)
        self._filter_sun(filters)
        self._filter_acquisition(filters)
        return self._search_default(spire_id, from_date, to_date, filters, size_limit)

class RawBeaconsQuery(ESQuery):
    def __init__(self, name, pwd):
        ESQuery.__init__(self, name, pwd)
    
    def search(self, spire_id, from_date, to_date):
        filters = {}
        _must = [
                { "constant_score": { "filter" : { "missing" : { "field" : "meta.beacon_processed" }}}},
                { "term" : { "_type" : "flowgraph" }}
            ]
        self._add_to_filters("must", _must, filters)
        self._filter_default(spire_id, from_date, to_date, filters)
        
        _query = {
            "query": {
                "bool": {
                    "must": _must,
                }
            },
                             
            "sort": [
                { "meta.log_time" : { "order": "asc" } },
            ]    
        }
        
        for key, value in enumerate(filters):
            _query["query"]["bool"][key] = value
        
        self.query = _query
        return self._search()


def flatten_results(search_results, response_fields=None):
    def _fetch_value(d, subfield):
        for s in subfield.split("."):
            d = d[s]
        return d

    res = []
    for row in search_results['hits']['hits']:
        d = {}
        date = datetime.datetime.strptime(row['_source']['meta']['time'], "%Y-%m-%dT%H:%M:%S")
        d['time'] = date.strftime('%Y-%m-%d %H:%M:%S')
        if response_fields is not None:
            for field in response_fields:
                d[field] = _fetch_value(row['_source']['response'], field)
        else:
            for field, value in row['_source']['response'].iteritems():
                d[field] = value
                
        res.append(d)
    return res