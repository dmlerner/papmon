from dataclasses import dataclass
from utils import *
import sortedcollection

@dataclass
class PowerDatum:
    time: float # seconds
    power: float # watts

    def parse_line(line):
        time_ms, power_mw = map(int, line.split()) # use in prod
        #power_mw, time_ms = map(int, line.split()) # old data file is backwards

        # sanity check on input order
        assert time_ms > power_mw

        return PowerDatum(time_ms/1000, power_mw/1000)

class PowerData(sortedcollection.SortedCollection):
    # TODO: saveable? 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, key=lambda d: t.time)

    def average_power(self, start, stop):
        te = self.get_time_and_energy(start, stop)
        if te is None: # TODO
            return 0
        time, energy = te
        return energy / time

    def get_energy(self, start, stop):
        return get_time_and_energy(self, start, stop)[1]

    def get_time_and_energy(self, start, stop):
        debug('get_time_and_energy')
        try:
            energy = 0
            if not len(self) >= 2:
                return None
            start_index = self.find_gt(now() - start)
            stop_index = self.find_lt(now() - stop)
            start_datum = self[start_index]
            start_time = start_datum.time
            for datum in self[start_index: stop_index]:
                dt = datum.time - start_datum.time
                power = (datum.power + start_datum.power) / 2
                energy += power * dt
            elapsed_time = datum.time - start_time
            return elapsed_time, energy
        except:
            # TODO, due to find_lt fialur eprobably
            debug('get_time_and_energy error', self, start, stop)
