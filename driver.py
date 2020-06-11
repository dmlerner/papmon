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

def main():
    debug('main')
    with contextlib.closing(PAPMonitor('data/resmed', '23:00', '6:00')) as pm:
        pm.poll_monitor()

if __name__ == '__main__':
    main()
