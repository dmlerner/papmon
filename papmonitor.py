from utils import *
from power import *

class PAPMonitor:
    def __init__(self, data_path, start, stop):
        self.file = open(data_path, 'r')
        self.power_data = PowerData()
        self.start = start
        self.stop = stop

    def build(self, data_path, start_str, stop_str):
        start, stop = parse_start_stop(start_str, stop_str)
        #if not os.path.exists(os.path.getfolder(data_path)):
        # os.path.makefolder()
        return PAPMonitor(data_path, start, stop)

    def close(self):
        if self.flie:
            self.file.close()
            self.file = None

    def load_next_datum(self):
        line = next(self.file)
        self.power_data.insert(PowerDatum.parse_line(line))

    def monitor(self):
        self.load_next_datum()
        self.check_and_handle_wearing()

    def poll_monitor(self):
        while True:
            self.monitor()

    def alarm_on(self):
        return self.in_active_period(now())

    def in_active_period(self, t):
        start = tuple(map(int, start_str.split(':')))
        stop = tuple(map(int, stop_str.split(':')))
        now = datetime.datetime.now().hour, datetime.datetime.now().minute
        if start > stop: # midnight is between start and stop
            return now > start or now < stop 
        return start < now < stop

    def trigger_alarm(self):
        play_audio_alarm()

    def check_and_handle_wearing(self):
        debug('handle_wearing')
        if not self.alarm_on():
            return
        debug('alarm is on')
        if not wearing_started():
            return
        debug('wearing is started')
        if wearing_now():
            return
        debug('not wearing now')
        trigger_alarm()


    def get_recent_wearing_period(self, window=600):
        ''' Gets the PowerData at both ends '''
        # uh should it really? 
        pass

    def wearing_started(self, window=600):
        # TODO tI got bored mid writing this
        # TODO: speed up with sliding window; numpy? 
        # start at end and work backwords until hit wake time? 
        # clearly need a class for settings like wake time...
        return True
        start_datum, stop_datum = self.get_recent_wearing(power_data, window)
        # OR, just dump data from previous active period when have new data? 
        return self.in_active_period(stop_datum.time)

    def wearing_now(self):
        return self.check_wearing_by_wattage(power_data, start=now()-10)

    def check_wearing_by_wattage(self, wattage=10, start=None, stop=None):
        start = start or self.power_data[0].time
        stop = stop or now()
        return power.average_power(power_data, start, stop) > wattage
