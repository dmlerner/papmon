import time
import os
from . import chromecast
import datetime

import logging
logger = logging.getLogger(__name__)

class Alarm(chromecast.ChromeCast):
    def __init__(self, name, media_path=None):
        super().__init__(name)
        self.media_path = media_path

    def play(self, media_path=None):
        logger.info('media_path %s', media_path)
        path = media_path or self.media_path
        assert path
        super().play(path)

    def is_going_off(self):
        return self.is_playing()
