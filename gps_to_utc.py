#!/usr/bin/python
# encoding: utf-8

import datetime

def convert(wk, ms):
    LEAP_SECONDS = 17
    return datetime.datetime.utcfromtimestamp(wk * 604800 + ms / 1000.0 + 315964800 - LEAP_SECONDS)

if __name__ == '__main__':    
    gps_wk = 1867
    gps_ms = 435630000
    print(convert(gps_wk, gps_ms).strftime('%Y-%m-%d %H:%M:%S'))