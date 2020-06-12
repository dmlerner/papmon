import random
import glob
import pathlib
import time
import datetime
import contextlib

import logging
logger = logging.getLogger(__name__)

from . import power
from . import alarm
from .utils.utils import *

class PAPMonitor:
    #window_duration = datetime.timedelta(minutes=10)
    window_duration = datetime.timedelta(seconds=10)
    cutoff_power = 10

    def __init__(self, f, start, stop):
        self.file = f
        self.power_data = power.PowerData()
        self.start = start
        self.stop = stop
        self.alarm_going_off = False

    @staticmethod
    def parse_time_str(s):
        return datetime.time(*map(int, s.split(':')))


    @staticmethod
    def open_or_create(path):
        #if not os.path.exists(os.path.getfolder(data_path)):
        # os.path.makefolder()
        # TODO
        if type(path) is str:
            return open(path, 'r')
        return path # TODO rename

    @staticmethod
    def get_latest_data():
        package_folder = str(pathlib.Path(__file__).parent.absolute())
        data_path = glob.glob(str(package_folder) + '/../data/power/*')[-1]
        return open(data_path, 'r') 

    @staticmethod
    def build(start_str, stop_str):
        start, stop = map(PAPMonitor.parse_time_str, (start_str, stop_str))
        f = PAPMonitor.get_latest_data()
        return PAPMonitor(f, start, stop)

    @staticmethod
    def build_fake(start_str, stop_str, n, should_trigger):
        start, stop = map(PAPMonitor.parse_time_str, (start_str, stop_str))
        return PAPMonitor(get_fake_file(n, should_trigger), start, stop)

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def load_next_datum(self):
        line = next(self.file)
        datum = power.PowerDatum.parse_line(line)
        self.power_data.insert(datum)
        return datum

    def load_data(self):
        data = power.PowerData()
        while True:
            try:
                data.insert(self.load_next_datum())
            except StopIteration:
                break
        return data

    def monitor(self):
        # Not currently using the new data directly
        data = self.load_data()
        # Checks old + new data, ie self.power_data
        self.check_and_handle_wearing()

    def poll_monitor(self, dt=1):
        while True:
            self.monitor()
            time.sleep(dt)

    def alarm_on(self):
        ''' May check additional criteria, eg phone is at home '''
        return self.in_active_period()

    def get_active_period(self, t=None):
        ''' Get last active period not ending before t '''
        t = t or now_datetime()
        assert type(t) is datetime.datetime
        stop = datetime.datetime.combine(t.date(), self.stop)
        if stop < t:
            stop += ONE_DAY
        start = datetime.datetime.combine(stop.date(), self.start)
        if start > stop:
            start -= ONE_DAY
        return start, stop

    def in_active_period(self, t=None):
        t = t or now_datetime()
        if type(t) is datetime.time:
            return in_active_period(on_today(t))
        assert type(t) is datetime.datetime

        start, stop = self.get_active_period(t)
        return start <= t <= stop

    def trigger_alarm(self):
        assert not self.alarm_going_off
        alarm.play_audio_alarm()
        self.alarm_going_off = True

    def check_and_handle_wearing(self):
        logger.debug('handle_wearing')
        if self.alarm_going_off:
            return
        if not self.alarm_on():
            return
        logger.debug('alarm is on')
        if not self.worn_in_active_period():
            return
        logger.debug('wearing is started')
        if self.wearing_now():
            return
        logger.debug('not wearing now')
        self.trigger_alarm()


    def worn_in_active_period(self):
        # TODO: speed up? 
        # start at end and work backwords until hit wake time? 
        if not self.in_active_period():
            return False
        over_cutoff_by_time = self.power_data.get_power_over_cutoff_by_start_time(
                *self.get_active_period(),
                PAPMonitor.window_duration,
                PAPMonitor.cutoff_power)
        return any(map(
            self.in_active_period,
            over_cutoff_by_time))

    def wearing_now(self):
        average_power = self.power_data.average_power(
                now_datetime() - PAPMonitor.window_duration,
                now_datetime()) 
        return average_power and average_power > PAPMonitor.cutoff_power

def get_fake_file(n=100, should_trigger=True):
        times = [str(time.time() - 3600*5*random.random()) for i in range(n)]
        times += [str(time.time() + 1000)]
        powers = [random.random() * 12 for i in range(n)] + [-20]
        data = [str(t) + ' ' + str(p) for (t, p) in zip(times, powers)]
        print(data[:5])
        return data.__iter__()

if __name__ == '__main__':
    pm = PAPMonitor.build_fake('11:00', '15:00', n=100, should_trigger=True)
    print(pm)
    pm.monitor()

