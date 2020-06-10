import os
import vlc
import time
import dataclasses
import sys
from sortedcollection import SortedCollection
import datetime

def debug(*args, **kwargs):
    #return
    print(*args, **kwargs, file=debug.file)

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


@dataclasses.dataclass
class PowerDatum:
    time: float # seconds
    power: float # watts

def average_power(power_data, start, stop):
    te = get_time_and_energy(power_data, start, stop)
    if te is None: # TODO
        return 0
    time, energy = te
    return energy / time

def get_energy(power_data, start, stop):
    return get_time_and_energy(power_data, start, stop)[1]

def get_time_and_energy(power_data, start, stop):
    print('get_time_and_energy')
    try:
        energy = 0
        if not len(power_data) >= 2:
            return None
        start_index = power_data.find_gt(now() - start)
        stop_index = power_data.find_lt(now() - stop)
        start_datum = power_data[start_index]
        start_time = start_datum.time
        for datum in power_data[start_index: stop_index]:
            dt = datum.time - start_datum.time
            power = (datum.power + start_datum.power) / 2
            energy += power * dt
        elapsed_time = datum.time - start_time
        return elapsed_time, energy
    except:
        # TODO, due to find_lt fialur eprobably
        debug('get_time_and_energy error', power_data, start, stop)

def check():
    debug('check')
    power_data = SortedCollection(key=lambda d: d.time)
    data_path = 'data/resmed'
    with open(data_path, 'r') as f:
        for line in get_read_generator(f):
            seconds, watts = parse_line(line)
            power_data.insert(PowerDatum(seconds, watts)) # TODO Saveable? 
            handle_wearing(power_data)

def play_audio_alarm():
    vlc = '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'
    filename = 'poet.mp3'
    os.system(vlc + ' ' + filename)

def in_active_period(t, start_str='23:00', stop_str='6:00'):
    start = tuple(map(int, start_str.split(':')))
    stop = tuple(map(int, stop_str.split(':')))
    now = datetime.datetime.now().hour, datetime.datetime.now().minute
    if start > stop: # midnight is between start and stop
        return now > start or now < stop 
    return start < now < stop

# TODO: input/output/etc decorator
def is_system_active(start_str='23:00', stop_str='6:00'):
    # TODO: double check this logic
    debug('is_system_active', start_str, stop_str)
    return in_active_period(now())

def get_recent_wearing_period(power_data, window=600):
    ''' Gets the PowerData at both ends '''
    pass

def wearing_started(power_data, window=600):
    # TODO tI got bored mid writing this
    # TODO: speed up with sliding window; numpy? 
    # start at end and work backwords until hit wake time? 
    # clearly need a class for settings like wake time...
    return True
    start_datum, stop_datum = get_recent_wearing(power_data, window)
    return in_active_period(stop_datum.time)

def wearing_now(power_data):
    return check_wearing_by_wattage(power_data, start=now()-10)

def check_wearing_by_wattage(power_data, wattage=10, start=None, stop=None):
    start = start or power_data[0].time
    stop = stop or now()
    return average_power(power_data, start, stop) > wattage

def handle_wearing(power_data):
    debug('handle_wearing')
    if not is_system_active():
        return
    if not wearing_started(power_data):
        return
    if wearing_now(power_data):
        return
    play_audio_alarm()

def main():
    with open('driver.debug', 'a') as f:
        debug.file = f
        debug('main')

        # manage via common run.sh instead
        # start_power_polling()
        # TODO: close poll ever? 

        check()


if __name__ == '__main__':
    main()
