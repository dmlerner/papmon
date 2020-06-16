from dataclasses import dataclass
import datetime

import logging
logger = logging.getLogger(__name__)

from .sortedcollection import SortedCollection
from .utils import utils

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

    def __str__(self):
        return 'PowerDatum[%s][%s]' % (self.timestamp.strftime('%H:%M:%S'), self.power)

class EnergyDatum(PowerDatum):
    def __init__(self, timestamp, power, energy):
        super().__init__(timestamp, power)
        self.energy = energy

    @staticmethod
    def build(pd1, pd2):
        elapsed_time = utils.get_elapsed_time(pd1, pd2)
        average_power = utils.average(pd1.power, pd2.power)
        average_timestamp = utils.average(pd1.timestamp, pd2.timestamp)
        energy = average_power * elapsed_time.total_seconds()
        return EnergyDatum(
                average_timestamp,
                average_power,
                energy)

    def __str__(self):
        return 'EnergyDatum[%s][%s][%s]' % (
                self.timestamp.strftime('%H:%M:%S'), 
                self.energy,
                self.power)

class PowerData(SortedCollection):
    def __str__(self):
        return 'PowerData[%s][%s][%s]'%(str(len(self)), str(list(map(str, self[:5]))), str(list(map(str, self[-5:]))))
    # TODO: saveable? 

    def __init__(self, *args, **kwargs):
        kwargs['key'] = kwargs.get('key') or (lambda pd: pd.timestamp) # TODO copy
        super().__init__(*args, **kwargs)

    def average_power(self, start, stop):
        logger.debug('start %s', start)
        logger.debug('stop %s', stop)
        sums = self.get_energy_prefix_sums(start, stop)
        # TODO: obob with energy? 
        if not sums:
            return
        if len(sums) == 1:
            return sums[0].power
        return sums[-1].energy / utils.get_elapsed_time(sums[0], sums[-1]).total_seconds()

    def check_bounds(self, start, stop):
        logger.debug('check_bounds %s %s %s', self, start, stop)
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
        except ValueError as e:
            logger.error('get energy bound error %s', e)
            return PowerData()
        start_index = self.find_ge_index(start) 
        logger.debug('start_index %s', start_index)
        stop_index = self.find_le_index(stop) 
        logger.debug('stop_index %s', stop_index)
        return PowerData(EnergyDatum.build(*self[i: i+2])  # TODO: EnergyData?
                for i in range(start_index, stop_index - 1))

    def get_energy_prefix_sums(self, start, stop):
        logger.debug('start, stop %s %s', start, stop)
        energies = self.get_energies(start, stop)
        logger.debug('energies %s', energies)
        for i in range(1, len(energies)):
            energies[i].energy += energies[i-1].energy
        return energies

    def get_power_over_cutoff_by_start_time(self, start, stop, window_duration, cutoff):
        assert set(map(type, (start, stop))) == {datetime.datetime}
        assert type(window_duration) is datetime.timedelta
        assert type(cutoff) in (float, int)
        power_by_start_time = self.get_power_by_start_time(start, stop, window_duration)
        logger.debug('power_by_start_time %s %s', str(power_by_start_time)[:200], str(power_by_start_time)[-200:])
        return dict(filter(
            lambda kv: kv[1] > cutoff,
            power_by_start_time.items()))

    def get_power_by_start_time(self, start, stop, window_duration):
        prefix_sums = self.get_energy_prefix_sums(start, stop)
        logger.debug('prefix_sums %s', prefix_sums)
        power_by_start_time = {}
        for start_e in prefix_sums:
            try:
                stop_e = prefix_sums.find_le(start_e.timestamp + window_duration)
            except ValueError:
                break
            duration = utils.get_elapsed_time(start_e, stop_e)
            if duration.total_seconds() == 0:
                if start_e is not stop_e:
                    logger.debug('two same time data, weird! %s %s', start_e, stop_e)
                power_by_start_time[start_e.timestamp] = start_e.power
            else:
                energy = stop_e.energy - start_e.energy
                average_power = energy/duration.total_seconds()
                power_by_start_time[start_e.timestamp] = average_power
        #logger.debug('power_by_start_time %s', power_by_start_time)
        return power_by_start_time
