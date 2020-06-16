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

    def __init__(self, f, start, stop,
            window_duration = datetime.timedelta(minutes=10),
            cutoff_power = 10,
            ):
        self.file = f
        self.power_data = power.PowerData()
        self.start = start
        self.stop = stop
        self.alarm_going_off = False
        self.window_duration = window_duration
        self.cutoff_power = cutoff_power

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
    def build(start_str, stop_str, window_duration):
        start, stop = map(PAPMonitor.parse_time_str, (start_str, stop_str))
        f = PAPMonitor.get_latest_data()
        window_duration = PAPMonitor.parse_window_duration(window_duration)
        return PAPMonitor(f, start, stop, window_duration)

    @staticmethod
    def parse_window_duration(d):
        if type(d) is datetime.timedelta:
            return d
        if type(d) is str:
            num = float(d[:-1])
            suffix = d[-1]
            if suffix == 'm':
                return datetime.timedelta(minutes=num)
            assert d[-1] == 's'
            return datetime.timedelta(seconds=num)
        return datetime.timedelta(seconds=num)

    @staticmethod
    def build_fake(should_trigger):
        now = datetime.datetime.now()
        start = (now - datetime.timedelta(hours=2)).strftime('%H:%m')
        if should_trigger:
            stop = (now + datetime.timedelta(hours=1)).strftime('%H:%m')
        else:
            stop = (now - datetime.timedelta(hours=1)).strftime('%H:%m')
        return PAPMonitor(get_fake_file(should_trigger), start, stop)

    def close(self):
        logger.debug('closing')
        if self.file:
            self.file.close()
            self.file = None

    def load_next_datum(self):
        line = next(self.file)
        logger.debug('datum loaded for line: %s', line)
        datum = power.PowerDatum.parse_line(line)
        logger.debug('datum parsed as: %s', datum)
        self.power_data.insert(datum)
        return datum

    def load_data(self):
        data = power.PowerData()
        while True:
            try:
                data.insert(self.load_next_datum())
            except StopIteration as e:
                # TODO: get new latest file?  even when no error? 
                logger.debug('stop iteration %s', e)
                break
        logger.debug('loaded new data %s', data)
        return data

    def monitor(self):
        data = self.load_data()
        # Checks old + new data, ie self.power_data
        self.check_and_handle_wearing()

    def poll_monitor(self, dt=1):
        while True:
            try:
                self.monitor()
            except BaseException as e:
                logger.error('monitor error %s', e)
            time.sleep(dt)

    def alarm_on(self):
        ''' May check additional criteria, eg phone is at home '''
        return self.in_active_period()

    def get_active_period(self, t=None):
        ''' Get last active period not ending before t '''
        logger.debug('get active period t %s', t)
        t = t or now_datetime()
        assert type(t) is datetime.datetime
        stop = datetime.datetime.combine(t.date(), self.stop)
        if stop < t:
            stop += ONE_DAY
        start = datetime.datetime.combine(stop.date(), self.start)
        if start > stop:
            start -= ONE_DAY
        logger.debug('active period: start %s stop %s', start, stop)
        return start, stop

    def in_active_period(self, t=None):
        logger.debug('in active period t %s', t)
        t = t or now_datetime()
        if type(t) is datetime.time:
            return in_active_period(on_today(t))
        assert type(t) is datetime.datetime

        start, stop = self.get_active_period(t)
        logger.debug('in active period returning: %s', start <= t <= stop)
        return start <= t <= stop

    def trigger_alarm(self):
        assert not self.alarm_going_off
        alarm.play_audio_alarm()
        #self.alarm_going_off = True

    def check_and_handle_wearing(self):
        logger.debug('handle_wearing, papmonitor=%s', self)
        if self.alarm_going_off:
            return
        logger.debug('alarm not going off yet')
        if not self.alarm_on():
            return
        logger.debug('alarm is armed')
        if not self.worn_in_active_period():
            return
        logger.debug('has been worn in active period')
        if self.wearing_now():
            return
        logger.debug('not wearing now')
        self.trigger_alarm()
        logger.debug('triggered alarm')


    def worn_in_active_period(self):
        # TODO: speed up? 
        # start at end and work backwords until hit wake time? 
        logger.debug('worn in active period')
        if not self.in_active_period():
            return False
        logger.debug('in active period')
        over_cutoff_by_time = self.power_data.get_power_over_cutoff_by_start_time(
                *self.get_active_period(),
                self.window_duration,
                self.cutoff_power)
        return any(map(
            self.in_active_period,
            over_cutoff_by_time))

    def wearing_now(self):
        average_power = self.power_data.average_power(
                now_datetime() - self.window_duration,
                now_datetime()) 
        return average_power and average_power > self.cutoff_power

    def __str__(self):
        return 'PAPMonitor[%s]' % self.power_data

def get_fake_file(should_trigger=True):
    n = 100
    times = [str(time.time() - 3600*5*random.random()) for i in range(n)]
    powers = [random.random() * 12 for i in range(n)] 
    if should_trigger:
        times += [str(time.time() + 1000)]
        powers += [-200000]
    data = [str(t) + ' ' + str(p) for (t, p) in zip(times, powers)]
    logger.debug('data %s %s', data[:5], data[-1])
    return data.__iter__()

if __name__ == '__main__':
    pm = PAPMonitor.build_fake(should_trigger=True)
    print(pm)
    pm.monitor()

