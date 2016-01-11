#!/usr/bin/python
# encoding: utf-8

import requests

import json
import csv

class InfluxQuery:
    def __init__(self, url, db):
        self.init_url = '/'.join([url, 'query?pretty=true'])
        self.db = db

    def _make_query(self, ):
    def _filter_default(self, spire_id, from_date, to_date, filters):
        filters['cond'].append('spire_id = %s' % spire_id)
        filters['cond'].append('time >= \'%s\'' % from_date)
        filters['cond'].append('time <= \'%s\'' % to_date)
        
    def _search(self):
        res = requests.get('&'.join([init_url, 'db=%s' % self.db, 'q=%s' % self.query]))

    def _search_default(self, spire_id, from_date, to_date, filters, size_limit=10000000):
        self._filter_default(spire_id, from_date, to_date, filters)
        self._make_query(filters, size_limit)
        return self._search(size_limit)
