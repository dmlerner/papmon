from utils import *
import datetime
import power
import alarm

class PAPMonitor:
    def __init__(self, data_path, start, stop):
        self.file = open(data_path, 'r')
        self.power_data = power.PowerData()
        self.start = start
        self.stop = stop

    @staticmethod
    def parse_time_str(s):
        return datetime.time(*map(int, s.split(':')))


    @staticmethod
    def check_exists(path):
        #if not os.path.exists(os.path.getfolder(data_path)):
        # os.path.makefolder()
        # TODO
        pass

    @staticmethod
    def build(data_path, start_str, stop_str):
        start, stop = map(PAPMonitor.parse_time_str, (start_str, stop_str))
        PAPMonitor.check_exists(data_path) # TODO move to utils
        return PAPMonitor(data_path, start, stop)


    def close(self):
        if self.file:
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
        ''' May check additional criteria, eg phone is at home '''
        return self.in_active_period()

    def in_active_period(self, t=None):
        t = t or now_time()
        t, start, stop = map(on_today, (t, self.start, self.stop))
        if start > stop: # midnight is between start and stop
            return t >= start or t <= stop 
        return start <= t <= stop

    def trigger_alarm(self):
        alarm.play_audio_alarm()

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

if __name__ == '__main__':
    p = PAPMonitor.build('data/resmed', '23:00', '6:00')
    p.close()
    for h in range(24):
        print(h, p.in_active_period(datetime.time(h, 1)))
    print(vars(p))
