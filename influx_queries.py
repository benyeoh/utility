#!/usr/bin/python
# encoding: utf-8

import requests
import datetime
import json
import csv

class InfluxQuery:
    def __init__(self, url, db):
        self.init_url = '/'.join([url, 'query?pretty=true'])
        self.db = db

    def _make_query(self, filters):
        if not filters.has_key('field'):
            self._add_filter(filters, 'field', '*')            
        self.query = 'SELECT %s FROM %s' % (','.join(filters['field']), ','.join(filters['table']))
        if filters.has_key('cond'):
            self.query += ' WHERE %s' % (' AND '.join(filters['cond']))
        
        self.query += ' ORDER BY time ASC'
        if filters.has_key('limit'):
            self.query += ' LIMIT %d' % (filters['limit'][0])        
        
    def _add_filter(self, filters, key, value):
        if not filters.has_key(key):
            filters[key] = []    
        
        if type(value) is list:
            filters[key].extend(value)
        else:
            filters[key].extend([value,])
                 
    def _filter_default(self, spire_id, from_date, to_date, filters):
        self._add_filter(filters, 'cond', 'spire_id = \'%s\'' % spire_id)
        self._add_filter(filters, 'cond', 'time >= \'%s\'' % from_date)
        self._add_filter(filters, 'cond', 'time <= \'%s\'' % to_date)
        
    def _search(self):
        res = requests.get('&'.join([self.init_url, 'db=%s' % self.db, 'q=%s' % self.query]))
        return res
    
    def _search_default(self, spire_id, from_date, to_date, filters, size_limit):
        self._filter_default(spire_id, from_date, to_date, filters)
        self._add_filter(filters, 'limit', size_limit)        
        self._make_query(filters)
        return self._search()

class ADACSQuery(InfluxQuery):
    def __init__(self, url, db):
        InfluxQuery.__init__(self, url, db)
        
    def _filter_type(self, filters):
        _type = ['/mai400_std.*/', '/mai400_ehs.*/', '/mai400_rot.*/', '/mai400_imu.*/']
        self._add_filter(filters, 'table', _type)

    def search(self, spire_id, from_date, to_date, size_limit=10000000, variant=''):
        if variant != '':
            func = getattr(self, 'search_%s' % variant)
            if func is not None:
                return func(spire_id, from_date, to_date, size_limit)
        filters = {}
        self._filter_type(filters)
        return self._search_default(spire_id, from_date, to_date, filters, size_limit)
    
class GPSQuery(InfluxQuery):
    def __init__(self, url, db):
        InfluxQuery.__init__(self, url, db)
        
    def _filter_type(self, filters):
        _type = '/gps_pos_vel.*/'
        self._add_filter(filters, 'table', _type)

    def search(self, spire_id, from_date, to_date, size_limit=10000000, variant=''):
        if variant != '':
            func = getattr(self, 'search_%s' % variant)
            if func is not None:
                return func(spire_id, from_date, to_date, size_limit)

        filters = {}
        self._filter_type(filters)
        return self._search_default(spire_id, from_date, to_date, filters, size_limit)

def flatten_results(search_results, filter_fields=None):
    def _fetch_value(d, subfield):
        for s in subfield.split("."):
            d = d[s]
        return d
    
    if not search_results['results'][0].has_key('series'):
        return None
    
    # Combine all columns from all tables
    combined_column_names = []
    for table in search_results['results'][0]['series']:
        for column in table['columns']:
            if column not in combined_column_names:
                combined_column_names.append(column)
    
    # Create dictionary of row values for each table
    flattened_tables = {}
    for table in search_results['results'][0]['series']:
        table_values = []
        for value in table['values']:
            table_value = {}
            for i, field in enumerate(value):
                column_name = table['columns'][i]
                if column_name == 'time':
                    date = datetime.datetime.strptime(field, "%Y-%m-%dT%H:%M:%SZ")
                    field = ((date-datetime.datetime(1970, 1, 1)).total_seconds())
        
                table_value[table['columns'][i]] = field
            table_values.append(table_value)
        flattened_tables[table['name']] = {'values' : table_values, 'cur_index' : 0 } 

    def _is_all_values_sorted(tables):
        for table in tables.itervalues():
            if table['cur_index'] < len(table['values']):
                return False
        return True
    
    def _get_record_with_next_time(tables):
        cur_table = None
        for table in tables.itervalues():
            if table['cur_index'] < len(table['values']):
                if cur_table is not None:
                    cur_min_time = cur_table['values'][cur_table['cur_index']]['time']
                    if table['values'][table['cur_index']]['time'] < cur_min_time:
                        cur_table = table
                else:
                    cur_table = table
        if cur_table is not None:
            cur_record = cur_table['values'][cur_table['cur_index']]
            cur_table['cur_index'] += 1
            return cur_record    
        return None
     
    # Join and sort tables (assuming each table is already pre-sorted)
    combined_table_values = []
    while not _is_all_values_sorted(flattened_tables):
        combined_value = {}
        next_value = _get_record_with_next_time(flattened_tables)
        for column_name in combined_column_names:
            if next_value.has_key(column_name):
                combined_value[column_name] = next_value[column_name]
            else: 
                combined_value[column_name] = None
        date = datetime.datetime.utcfromtimestamp(combined_value['time'])
        combined_value['time'] = date.strftime('%Y-%m-%d %H:%M:%S')  
        combined_table_values.append(combined_value)

    # Finally filter only the fields we want
    filtered_table_values = []
    if filter_fields is not None:
        for value in combined_table_values:
            filtered_value = {}
            filtered_value['time'] = value['time']       
            num_null_fields = 0
            for field in filter_fields:
                actual_val = _fetch_value(value, field)
                if actual_val is None:
                    num_null_fields += 1
                filtered_value[field] = actual_val                         
            # We are only interested in non-null fields
            if num_null_fields < len(filter_fields):
                filtered_table_values.append(filtered_value)     
        return filtered_table_values
        
    return combined_table_values

