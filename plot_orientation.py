#!/usr/bin/python
# encoding: utf-8

import warnings
import base64

import json
import optparse
import csv
import sys
import time
import datetime
import re

import math
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class QBOEntry:
    def __init__(self, time, qbo):
        self.time = time
        self.qbo = qbo
            
    def extract_euler(self):
        q = self.qbo
        q0 = q[3]
        q1 = q[0]
        q2 = q[1]
        q3 = q[2]
        roll = math.atan2(2.0*(q0*q1+q2*q3), 1.0 - 2.0*(q1*q1 + q2*q2))
        pitch = math.asin(2.0*(q0*q2 - q3*q1))
        yaw = math.atan2(2.0*(q0*q3 + q1*q2), 1.0 - 2.0*(q2*q2 + q3*q3))

        return (yaw, pitch, roll)

    def extract_body_neg_y(self):
        q = self.qbo
        b = q[0]
        c = q[1]
        d = q[2]
        a = q[3]
        
        y0 = 2.0*b*c - 2.0*a*d
        y1 = a*a - b*b + c*c - d*d
        y2 = 2.0*c*d + 2.0*a*b
        return (-y0, -y1, -y2)
        
def plot_qbo_data(qbo_data, title, overlay_data=None, is_mod_24_hrs=False):
    # Get dates modulo 24 hrs
    time_stamps = []
    euler_yaw = []
    euler_pitch = []
    euler_roll = []
    neg_y_facing = []
    dates = []
    
    for d in qbo_data:
        if is_mod_24_hrs:
            time_stamps.append((d.time.hour * 60 * 60 + d.time.minute * 60 + d.time.second) / 3600.0)
        #time_stamps.append((d.time-datetime.datetime(1970, 1, 1)).total_seconds() / 86400.0)
        dates.append(d.time)        
        euler = d.extract_euler()
        euler_yaw.append(euler[0])
        euler_pitch.append(euler[1])
        euler_roll.append(euler[2])

        neg_y = d.extract_body_neg_y()
        neg_y_facing.append(neg_y[2])
        
    ax = plt.subplot(411)
    plt.ylabel('Angle (Radians)')
    if is_mod_24_hrs:
        plt.title('Yaw (Time Modulo 24 Hrs)')
        plt.plot(time_stamps, euler_yaw, 'ro')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))
    else:
        plt.title('Yaw')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, euler_yaw, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        plt.gcf().autofmt_xdate()
        
    ax = plt.subplot(412)
    plt.ylabel('Angle (Radians)')
    if is_mod_24_hrs:
        plt.title('Pitch (Time Modulo 24 Hrs)')
        plt.plot(time_stamps, euler_pitch, 'ro')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))
    else:
        plt.title('Pitch')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, euler_pitch, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        plt.gcf().autofmt_xdate()
    
    ax = plt.subplot(413)
    plt.ylabel('Angle (Radians)')
    if is_mod_24_hrs:
        plt.title('Roll (Time Modulo 24 Hrs)')
        plt.plot(time_stamps, euler_roll, 'ro')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))    
    else:
        plt.title('Roll')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, euler_roll, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        plt.gcf().autofmt_xdate()
    
    ax = plt.subplot(414)
    plt.title('GPS Antenna Facing, Body -Y Axis (-ve facing away from Earth, +ve facing towards Earth)')
    plt.ylabel('Orbit Frame Z')
    if is_mod_24_hrs:
        plt.plot(time_stamps, neg_y_facing, 'ro')
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(numpy.arange(start, end, 1.0))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.plot(dates, neg_y_facing, 'ro')
        if overlay_data is not None:
            for overlay in overlay_data:           
                ax.axvspan(*mdates.date2num([overlay['start'], overlay['end']]), color='red', alpha=0.5)
        plt.gcf().autofmt_xdate()
    
    plt.tight_layout()       
    plt.suptitle(title, size=16)
    plt.show()

def extract_qbo(data):
    qbo_data = []
    
    for d in data:                        
        dt = datetime.datetime.strptime(d["time"], "%Y-%m-%d %H:%M:%S")
        #epoch_timestamp = ((dt-datetime.datetime(1970, 1, 1)).total_seconds())
        # Remove crap from qbo_hat_str
        
        if d['qbo_hat'] is not None and d['qbo_hat'] != '':
            qbo_hat_str = re.sub('[\[\]]', '', d["qbo_hat"]).split(',')
            qbo_hat = [float(val.strip()) for val in qbo_hat_str]
        else:
            qbo_hat = [float(d['qbo_hat_0']), float(d['qbo_hat_1']), float(d['qbo_hat_2']), float(d['qbo_hat_3'])]
            qbo_hat[0] *= (1.0 / 32767)
            qbo_hat[1] *= (1.0 / 32767)
            qbo_hat[2] *= (1.0 / 32767)
            qbo_hat[3] *= (1.0 / 32767)
            
        #if d["_source.response.acs_op_mode_str"] != 'NOOP':
        qbo_data.append( QBOEntry(dt, qbo_hat) )
        
    for d in qbo_data:
        #print("Date: %s, QBO: [%f, %f, %f, %f]" % (d.time, d.qbo[0], d.qbo[1], d.qbo[2], d.qbo[3]))
        euler = d.extract_euler()
        neg_y = d.extract_body_neg_y()
        #print("Date: %s, Euler: [%f, %f, %f], Neg Y: [%f, %f, %f]" % (d.time, euler[0], euler[1], euler[2], neg_y[0], neg_y[1], neg_y[2]))

    return qbo_data

def extract_overlay_times(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        data = [r for r in reader]
        overlay_times_data = [ 
                              {
                                'start' : datetime.datetime.strptime(d['start'], "%Y-%m-%d %H:%M:%S"),
                                'end' : datetime.datetime.strptime(d['end'], "%Y-%m-%d %H:%M:%S") 
                               } for d in data 
                             ]        
        return overlay_times_data
    return None

if __name__ ==  '__main__':
    # Handle option parsing
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-f', '--file', dest='file', help='CSV file input', 
                          metavar='FILE', default='')
    opt_parser.add_option('-o', '--overlay', dest='overlay', help='CSV file for overlay input', 
                          metavar='OVERLAY', default='')
      
    (opt_args, args) = opt_parser.parse_args()
    
    if opt_args.file != '':
        fm_str = opt_args.file.split('/')[-1].split('_')[0].upper()
        
        overlay_times = None
        if opt_args.overlay != '':
            overlay_times = extract_overlay_times(opt_args.overlay)
            
        with open(opt_args.file, 'r') as f:
            reader = csv.DictReader(f)
            data = [r for r in reader]
            qbo_data = extract_qbo(data)
            plot_qbo_data(qbo_data, '%s QBO Plot' % (fm_str), overlay_data=overlay_times, is_mod_24_hrs=True)
            