from dataclasses import dataclass
import datetime

from .sortedcollection import SortedCollection
from .utils import *

@dataclass
class PowerDatum:
    timestamp: datetime.datetime # seconds since the epoch
    power: float # Watts

    @staticmethod
    def parse_line(line):
        timestamp, watts = map(float, line.split()) # use in prod

        # sanity check on input order
        assert timestamp > watts

        return PowerDatum(
                datetime.datetime.fromtimestamp(timestamp),
                watts)

    #def __lt__(self, other):
        #return self.timestamp < other.timestamp

class EnergyDatum(PowerDatum):
    def __init__(self, timestamp, power, energy):
        super().__init__(timestamp, power)
        self.energy = energy

    @staticmethod
    def build(pd1, pd2):
        elapsed_time = get_elapsed_time(pd1, pd2)
        average_power = average(pd1.power, pd2.power)
        average_timestamp = average(pd1.timestamp, pd2.timestamp)
        energy = average_power * elapsed_time.total_seconds()
        return EnergyDatum(
                average_timestamp,
                average_power,
                energy)

class PowerData(SortedCollection):
    def __str__(self):
        return 'PowerData ' + str(list(self[:5])) + '...' + str(len(self))
    # TODO: saveable? 
    def __init__(self, *args, **kwargs):
        kwargs['key'] = kwargs.get('key') or (lambda pd: pd.timestamp) # TODO copy
        super().__init__(*args, **kwargs)

    def average_power(self, start, stop):
        sums = self.get_energy_prefix_sums(start, stop)
        # TODO: obob with energy? 
        if not sums:
            return
        if len(sums) == 1:
            return sums[0].power
        return sums[-1].energy / get_elapsed_time(sums[0], sums[-1]).total_seconds()

    def get_energy(self, start, stop):
        prefixes = self.get_energy_prefix_sums(start, stop)[-1].energy

    def check_bounds(self, start, stop):
        print('check_bounds', self, start, stop)
        if not self:
            raise ValueError('empty power data')
        if start > self.max().timestamp:
            raise ValueError('start after any time data')
        if stop < self.min().timestamp: 
            raise ValueError('stop before any time data')

    def get_energies(self, start, stop):
        # TODO: cache and invalidate on insert? 
        try:
            self.check_bounds(start, stop)
        except ValueError:
            return PowerData()
        start_index = self.find_ge_index(start) 
        print('start_index', start_index)
        stop_index = self.find_le_index(stop) 
        print('stop_index', stop_index)
        return PowerData(EnergyDatum.build(*self[i: i+2])  # TODO: EnergyData?
                for i in range(start_index, stop_index - 1))

    def get_energy_prefix_sums(self, start, stop):
        print('start, stop', start, stop)
        energies = self.get_energies(start, stop)
        print('energies', energies)
        for i in range(1, len(energies)):
            energies[i].energy += energies[i-1].energy
        return energies

    def get_power_over_cutoff_by_start_time(self, start, stop, window_duration, cutoff):
        assert set(map(type, (start, stop))) == {datetime.datetime}
        assert type(window_duration) is datetime.timedelta
        assert type(cutoff) in (float, int)
        power_by_start_time = self.get_power_by_start_time(start, stop, window_duration)
        return dict(filter(
            lambda kv: kv[1] > cutoff,
            power_by_start_time.items()))

    def get_power_by_start_time(self, start, stop, window_duration):
        prefix_sums = self.get_energy_prefix_sums(start, stop)
        print('prefix_sums', prefix_sums)
        power_by_start_time = {}
        for start_e in prefix_sums:
            try:
                stop_e = prefix_sums.find_le(start_e.timestamp + window_duration)
            except ValueError:
                break
            duration = get_elapsed_time(start_e, stop_e)
            if duration.total_seconds() == 0:
                print('duration 0, is?', start_e is stop_e)
                continue
            energy = stop_e.energy - start_e.energy
            average_power = energy/duration.total_seconds()
            power_by_start_time[start_e.timestamp] = average_power
        print('power_by_start_time', power_by_start_time)
        return power_by_start_time
