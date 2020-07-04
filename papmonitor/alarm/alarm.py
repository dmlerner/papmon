import time
import os
from . import chromecast
import datetime

import logging
logger = logging.getLogger('papmonitor')

class Alarm(chromecast.ChromeCast):
    def __init__(self, name, media_path=None):
        super().__init__(name)
        self.media_path = media_path

    def play(self, media_path=None):
        logger.info('media_path %s', media_path)
        path = media_path or self.media_path
        assert path
        logger.debug('mute')
        self.set_volume(0)
        logger.debug('play')
        super().play(path)
        logger.debug('smooth')
        self.smooth_set_volume(0, .7, steps=4, step_time=3)

    def is_going_off(self):
        logger.debug('volume: %s', self.get_volume())
        return self.is_playing()
