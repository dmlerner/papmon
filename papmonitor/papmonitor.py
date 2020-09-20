import random
import glob
import pathlib
import time
import datetime
import contextlib

import logging
logger = logging.getLogger('papmonitor')

from . import power
from .alarm.alarm import Alarm
from .utils.utils import *

class PAPMonitor:

    def __init__(self, f, start, stop,
            window_duration = datetime.timedelta(minutes=10),
            grace_period = datetime.timedelta(minutes=5),
            alarm = None,
            cutoff_power = 10,
            ):
        self.file = f
        self.power_data = power.PowerData(
                #[power.PowerDatum(datetime.datetime.now(), 0)]
                ) # need timestamp for staleness check
        self.start = start
        self.stop = stop
        self.window_duration = window_duration
        self.cutoff_power = cutoff_power
        self.time_taken_off = None
        self.alarm = alarm
        self.grace_period = grace_period

    @staticmethod
    def parse_time(s):
        return datetime.time(*map(int, s.split(':')))

    @staticmethod
    def get_root_path():
        package_folder = str(pathlib.Path(__file__).parent.absolute())
        return package_folder

    @staticmethod
    def get_latest_data_path():
        # glob comes out sorted, so this is last alphabetically, ie most recent
        return glob.glob(PAPMonitor.get_data_path()  + '/power/*')[-1]

    @staticmethod
    def get_data_path():
        return PAPMonitor.get_root_path() + '/../data'

    @staticmethod
    def get_snooze_path():
        return PAPMonitor.get_data_path() + '/snooze.txt'

    @staticmethod
    def get_latest_data():
        data_path = PAPMonitor.get_latest_data_path()
        logger.debug('data_path %s', data_path)
        return open(data_path, 'r')

    @staticmethod
    def build(start_str, stop_str, window_duration, grace, chromecast_name, media_path):
        start, stop = map(PAPMonitor.parse_time, (start_str, stop_str))
        window_duration = PAPMonitor.parse_duration(window_duration)
        grace = PAPMonitor.parse_duration(grace)
        alarm = Alarm(chromecast_name, media_path)
        return PAPMonitor(None, start, stop, window_duration, grace, alarm)

    @staticmethod
    def parse_duration(d):
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
        logger.debug('should_trigger %s', should_trigger)
        now = datetime.datetime.now()
        start = (now - datetime.timedelta(hours=2)).strftime('%H:%M')
        if should_trigger:
            stop = (now + datetime.timedelta(hours=1)).strftime('%H:%M')
            filename = 'file:///C:/Users/david/google-drive/coding/papmonitor/papmonitor/alarm/audio.mp3'
            alarm = Alarm('bedroom speaker', filename)
        else:
            stop = (now - datetime.timedelta(hours=1)).strftime('%H:%M')
            alarm = None

        return PAPMonitor(get_fake_file(should_trigger), start, stop, alarm=alarm)

    def close(self):
        logger.debug('closing')
        self.close_file()
        self.close_alarm()

    def close_file(self):
        if self.file:
            logger.debug('closing %s', self.file)
            self.file.close()
            self.file = None

    def close_alarm(self):
        if self.alarm:
            self.alarm.close()
            self.alarm = None

    def load_next_datum(self):
        if self.file is None:
            logger.debug('PAPMonitor.file is None')
            raise StopIteration('PAPMonitor.file is None')
        line = next(self.file)
        logger.debug('datum loaded for line: %s', line)
        datum = power.PowerDatum.parse_line(line)
        logger.debug('datum parsed as: %s', datum)
        self.power_data.insert(datum)
        return datum

    def should_reload(self):
        logger.debug('')
        if self.file is None:
            logger.debug('should reload; file is None')
            return True
        if self.file.name != self.get_latest_data_path():
            logger.debug('should reload; not using latest file')
            return True
        logger.debug('should not reload')

    def reload(self):
        logger.info('')
        self.close_file()
        self.file = PAPMonitor.get_latest_data()

    def load_data(self):
        if self.should_reload():
            self.reload()
        data = power.PowerData()
        while True:
            try:
                datum = self.load_next_datum()
                data.insert(datum)
            except StopIteration as e:
                logger.debug('stop iteration %s', e)
                assert not self.stale()
                break
        if data:
            logger.debug('loaded new data %s', data)
        else:
            logger.debug('no new data')
        return data

    def stale(self):
        # TODO: use self.window_duration?
        if not self.power_data:
            return False
        staleness = abs(self.power_data[-1].timestamp - datetime.datetime.now())
        logger.debug('staleness %s %s', self.file.name, staleness)
        msg = 'Data appears to no longer be updating'
        return staleness > datetime.timedelta(minutes=5)

    def monitor(self):
        data = self.load_data()
        # Checks old + new data, ie self.power_data
        self.check_and_handle_wearing()

    def poll_monitor(self, dt=1):
        while True:
            try:
                self.monitor()
            except BaseException as e:
                import traceback
                traceback.print_exc()
                logger.error('monitor error: %s', e)
            time.sleep(dt)

    def alarm_on(self):
        ''' May check additional criteria, eg phone is at home '''
        return not self.snoozed() and self.in_active_period()

    def get_active_period(self, t=None):
        ''' Get last active period not ending before t '''
        #logger.debug('get active period t %s', t)
        t = t or now_datetime()
        assert type(t) is datetime.datetime
        stop = datetime.datetime.combine(t.date(), self.stop)
        if stop < t:
            stop += ONE_DAY
        start = datetime.datetime.combine(stop.date(), self.start)
        if start > stop:
            start -= ONE_DAY
        #logger.debug('active period: start %s stop %s', start, stop)
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

    def should_alarm_be_going_off(self):
        logger.info('')
        logger.debug('check if: alarm is armed')
        if not self.alarm_on():
            logger.debug('check abort: alarm is not armed')
            return False
        logger.debug('check continue: alarm is armed')

        logger.debug('check if: has been worn in active period')
        if not self.worn_in_active_period():
            logger.debug('check abort: has not been worn in active period')
            return False
        logger.debug('check continue: has been worn in active period')

        logger.debug('check if: wearing now')
        if self.wearing_now():
            logger.debug('check abort: wearing now')
            return False
        logger.debug('check continue: not wearing now')

        logger.debug('check if: off long enough')
        if not self.off_long():
            logger.debug('check abort: not off long enough')
            return False
        logger.debug('check continue: off long enough')

        logger.info('alarm should be going off')
        return True


    def check_and_handle_wearing(self):
        logger.debug('handle_wearing, papmonitor=%s', self)
        should = self.should_alarm_be_going_off()
        logger.debug('should %s', should)

        logger.debug('check if: alarm is going off')
        if self.alarm.is_going_off():
            logger.debug('alarm is going off')
            if not should:
                logger.info('stopping alarm')
                self.alarm.stop()
        else:
            logger.debug('alarm is not going off')
            if should:
                logger.info('playing alarm')
                self.alarm.play() # TODO: thread for smooth set?

    def off_long(self):
        logger.debug('time_taken_off %s', self.time_taken_off)
        if not self.time_taken_off:
            return False
        logger.debug('elapsed: %s', abs(self.time_taken_off - now_datetime()))
        return abs(self.time_taken_off - now_datetime()) > self.grace_period


    def worn_in_active_period(self):
        # TODO: speed up?
        # start at end and work backwords until hit wake time?
        logger.debug('worn_in_active_period')
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
        wearing = average_power and average_power > self.cutoff_power
        if wearing:
            self.time_taken_off = None
        elif self.time_taken_off is None:
            self.time_taken_off = now_datetime()
        return wearing

    @staticmethod
    def snoozed():
        with open(PAPMonitor.get_snooze_path(), 'r') as f:
            snooze_until = datetime.datetime.fromisoformat(f.read())
        return datetime.datetime.now() < snooze_until

    @staticmethod
    def snooze_until(t=None, dt=None):
        if dt:
            assert not t
            assert isinstance(dt, datetime.timedelta)
            t = datetime.datetime.now() + dt
        t = t or datetime.datetime.now()
        assert isinstance(t, datetime.datetime)
        with open(PAPMonitor.get_snooze_path(), 'w+') as f:
            f.write(t.isoformat())

    @staticmethod
    def unsnooze():
        PAPMonitor.snooze_until() # Now

    def __str__(self):
        n = self.file.name if self.file is not None else 'None'
        return 'PAPMonitor[%s][%s][%s]' % (self.power_data, self.file.name, self.alarm)

def get_fake_file(should_trigger=True):
    n = 100
    times = [str(time.time() - 3600*5*random.random()) for i in range(n)]
    powers = [random.random() * 12 for i in range(n)]
    if should_trigger:
        times += [str(time.time() + 1)] # strong on
        powers += [2000000000000]
        times += [str(time.time() + 2)] # strongly off
        powers += [-2000000000000]
    data = [str(t) + ' ' + str(p) for (t, p) in zip(times, powers)]
    logger.debug('data %s %s', data[:5], data[-1])
    return data.__iter__()

if __name__ == '__main__':
    pm = PAPMonitor.build_fake(should_trigger=True)
    print(pm)
    pm.monitor()

