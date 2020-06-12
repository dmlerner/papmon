import os
import contextlib
import vlc
import time
import dataclasses
import sys
import datetime
from utils import *
from papmonitor import PAPMonitor


def main():
    debug('main')
    with contextlib.closing(PAPMonitor('data/resmed', '23:00', '6:00')) as pm:
        pm.poll_monitor()

if __name__ == '__main__':
    main()
