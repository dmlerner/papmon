import os
import contextlib
import vlc
import time
import dataclasses
import sys
from sortedcollection import SortedCollection
import datetime
from utils import *
from papmonitor import PAPMonitor


def now():
    #debug('now')
    return time.time()

def parse_line(line):
    time_ms, power_mw = map(int, line.split()) # use in prod
    #power_mw, time_ms = map(int, line.split()) # old data file is backwards

    # sanity check on input order
    assert time_ms > power_mw

    return time_ms/1000, power_mw/1000

def nowish(t, margin=10):
    debug('nowish', t, now())
    return abs(t - now()) < margin


def get_read_generator(f, sleep=.1):
    debug('get_file_tail')
    # https://stackoverflow.com/questions/5419888/reading-from-a-frequently-updated-file
    #f.seek(0,2) # WTF
    while True:
        line = f.readline()
        if not line:
            time.sleep(sleep)
            continue
        yield line


def check():
    debug('check')
    with open(data_path, 'r') as f:
        pass


def main():
    debug('main')
    with contextlib.closing(PAPMonitor('data/resmed', '23:00', '6:00')) as pm:
        pm.poll_monitor()

if __name__ == '__main__':
    main()
