#!/usr/bin/python
# encoding: utf-8

import datetime

gps_wk = 1867
gps_ms = 435630000

print(
    datetime.datetime.utcfromtimestamp(
        gps_wk * 604800 + gps_ms / 1000.0 + 315964800 - 17
    ).strftime('%Y-%m-%d %H:%M:%S')
)