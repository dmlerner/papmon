import os
import time
import dataclasses
import sys

def debug(*args, **kwargs):
    #return
    print('>>>', *args, **kwargs, file=debug.file)

def now():
    #debug('now')
    return time.time()

def parse_line(line):
    debug('parse_line')
    time_ms, power_mw = map(int, line.split()) # use in prod
    #power_mw, time_ms = map(int, line.split()) # old data file is backwards

    # sanity check on input order
    assert time_ms > power_mw

    return time_ms/1000, power_mw/1000

def nowish(t, margin=10):
    debug('nowish', t, now())
    return abs(t - now()) < margin


def get_file_tail(f, sleep=.1):
    debug('get_file_tail')
    # https://stackoverflow.com/questions/5419888/reading-from-a-frequently-updated-file
    f.seek(0,2) # WTF
    while True:
        line = f.readline()
        if not line:
            time.sleep(sleep)
            continue
        yield line

def seek_to_now(f, sleep=.1, margin=10):
    debug('seek_to_now')
    skipped = 0
    for line in get_file_tail(f, sleep):
        seconds, watts = parse_line(line)
        if not nowish(seconds, margin):
            skipped += 1
            continue
        skipped = 0
        if skipped:
            debug('skipped', skipped)
        yield seconds, watts

data_path = 'data/resmed'

def start_power_polling():
    debug('start_power_polling')
    # TODO check if ./data/resmed exists
    # TODO new file per day etc
    # begin writing (time in ms, wattage in milliwatts) 
    command = 'node poll.js'
    #subprocess.Popen(command.split(), stdout=subprocess.PIPE) # does not temrinate with script
    #return threading.Thread(target=lambda:os.system(command)).run()
    #os.system(command) # blocks



@dataclasses.dataclass
class PowerDatum:
    time: float # seconds
    power: float # watts
    energy: float # joules

def is_wearing(power_data, lookback_s=10):
    debug('is_wearing', power_data[:5])
    # TODO: detect oscillation? 
    # for now, look for wattage over cutoff
    joules = 0
    if not len(power_data) >= 2:
        return 
    for d in reversed(power_data):
        if abs(d.time - now()) > lookback_s:
            break
        joules += d.energy
    duration = power_data[-1].time - d.time # should be ~= lookback_s
    average_power = joules / duration
    cutoff_power = 10
    return average_power >= cutoff_power

def check():
    debug('check')
    power_data = []
    with open(data_path, 'r') as f:
        previous_seconds = None
        for seconds, watts in seek_to_now(f):
            if previous_seconds:
                assert seconds >= previous_seconds
                power_data.append(PowerDatum(seconds, watts, watts*(seconds - previous_seconds))) # TODO Saveable? 
                print(is_wearing(power_data))
            previous_seconds = seconds

def main():
    with open('driver.debug', 'a') as f:
        debug.file = f
        debug('main')
        start_power_polling()
        # TODO: close poll ever? 
        check()


if __name__ == '__main__':
    main()
