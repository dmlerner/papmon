import dataclasses

from utils import *

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
    debug('get_time_and_energy')
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

def parse_line(line):
    time_ms, power_mw = map(int, line.split()) # use in prod
    #power_mw, time_ms = map(int, line.split()) # old data file is backwards

    # sanity check on input order
    assert time_ms > power_mw

    return time_ms/1000, power_mw/1000
