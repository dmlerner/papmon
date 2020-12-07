import time
import os
import pdb
import threading


import pychromecast
import contextlib
from ..utils import wslprocess

import logging
logger = logging.getLogger('papmonitor')

class ChromeCast:

    @staticmethod
    def get_by_name(name):
        chromecasts = pychromecast.get_chromecasts()
        logger.debug('found chromecasts: %s',
                [c.device.friendly_name for c in chromecasts])
        for c in chromecasts:
            if c.device.friendly_name == name:
                return c

    def __init__(self, name):
        self.name = name
        self._chromecast = None
        self.vlc_pid = None # Windows side PID

    def ip(self):
        return self.get_chromecast().host

    def pause(self):
        return self.get_chromecast().media_controller.pause()

    def mute(self):
        return self.get_chromecast().set_volume_muted(True)

    def unmute(self):
        return self.get_chromecast().set_volume_muted(False)

    def set_volume(self, x): # float [0,1]
        return self.get_chromecast().set_volume(x)

    def status(self):
        return self.get_chromecast().status

    def canceled(self):
        # can't call get_chromecast; recursion
        if self._chromecast.media_controller.status.idle_reason == 'CANCELLED':
            # unclear why I need this...
            self._chromecast = None

    def get_chromecast(self):
        if self._chromecast is None or self.canceled():
            self._chromecast = ChromeCast.get_by_name(self.name)
        try:
            self._chromecast.wait()
        except:
            logger.debug('error waiting on chromecast %s', self._chromecast)
        return self._chromecast

    @staticmethod
    def get_player_path():
        # Underlying pychromecast.Chromecast.play_media expects a url
        # And I can't make it work with local media
        # Even with eg Python's http.server
        return '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'

    def get_play_flags(self):
        return (
                '-I dummy --dummy-quiet', # no gui
                '--play-and-exit',
                '--sout="#chromecast"',
                '--demux-filter=demux_chromecast',
                f'--sout-chromecast-ip={self.ip()}',
                '>cc.log 2>&1', # TODO: handle logging
                )

    def get_play_command(self, media_path):
        player_path = ChromeCast.get_player_path()
        flags = self.get_play_flags()
        return f'{player_path} {" ".join(flags)} {media_path} &'

    def play(self, media_path=None):
        logger.debug('play %s', media_path)
        if media_path is None:
            if self.is_playing():
                logger.debug('already playing')
                return
            if self.is_paused():
                self.unpause()
                return

        assert media_path
        self.stop()
        command = self.get_play_command(media_path)
        #pdb.set_trace()

        # logger.debug(self._chromecast.status)
        # logger.debug(self._chromecast.device)
        # mc = self._chromecast.media_controller
        # logger.debug(mc.status)

        # Needed to avoid connection noise
        logger.debug('muting')
        self.mute()
        logger.debug(command)
        existing_vlcs = wslprocess.get_pids('vlc')
        logger.debug('existing vlcs %s', existing_vlcs)
        os.system(command)
        #time.sleep(5)
        self.vlc_pid = (wslprocess.get_pids('vlc') - existing_vlcs).pop()
        logger.debug('new vlc %s', self.vlc_pid)
        logger.debug('waiting')
        self.wait_for_playing()
        logger.debug('unmuting')
        self.unmute()

    def wait_for_playing(self, timeout=10, sleep=.5):
        # TODO: threading
        logger.debug('')
        for i in range(int(timeout/sleep)):
            if self.is_playing():
                time.sleep(sleep)
                return
            logger.debug('sleeping')
            time.sleep(sleep)
        logger.debug('timed out waiting for play')
        logger.debug(self.status())
        logger.debug(self.get_chromecast().media_controller.status)
        assert False

    def stop(self):
        logger.debug('')
        self.get_chromecast().media_controller.stop()
        #wslprocess.kill_pids([self.vlc_pid])
        wslprocess.kill('vlc') # TODO: this is heavy handed, but shit's getting orphaned ...

    def unpause(self):
        logger.debug('')
        self.get_chromecast().media_controller.play()

    def close(self):
        logger.debug('')
        self.stop()
        self.get_chromecast().disconnect()

    def is_open(self):
        logger.debug('')
        return self.vlc_pid in wslprocess.get_pids('vlc')

    def media_status(self):
        return self.get_chromecast().media_controller.status

    def is_playing(self):
        logger.debug('media_controller status %s', self.get_chromecast().media_controller.status)
        return self.media_status().player_state == 'PLAYING'

    def is_paused(self):
        logger.debug('media_controller status %s', self.get_chromecast().media_controller.status)
        return self.media_status().player_state == 'PAUSED'

    def smooth_set_volume(self, start=None, target=None, steps=10, step_time=1):
        if start is None:
            start = self.get_volume()
        if target is None:
            target = 1
        self.set_volume(target)
        # warning: blocking!
        #return # TODO: needs caller to have threading or something...
        dv = (target - start) / steps
        for i in range(steps):
            v = start + i*dv
            logger.debug('smooth set, step %s, volume %s', i, v)
            self.set_volume(v)
            time.sleep(step_time)

    def get_volume(self):
        return self.media_status().volume_level


def main():
    logging.basicConfig(
            filename=None, # stdout
            level=logging.DEBUG,
            format='%(relativeCreated)-7d|%(levelname)-7s|%(module)-10s|%(lineno)-4d|%(funcName)-35s|%(message)s',
            )

    global c, cc, mc, filename
    #with contextlib.closing(ChromeCast('Bedroom speaker')) as c:
    c = ChromeCast('Bedroom speaker')
    #c = ChromeCast('Bike')
    cc = c.get_chromecast()
    mc = cc.media_controller
    #c = ChromeCast('Gym')
    logger.debug('play')
    filename = 'file:///C:/Users/david/google-drive/coding/papmonitor/papmonitor/alarm/audio.mp3'
    #import pdb; pdb.set_trace()

    c.set_volume(0)
    c.play(filename)
    c.smooth_set_volume(0, 1)
    return
    logger.debug('pause')
    c.pause()
    time.sleep(2)
    logger.debug('unpause')
    c.unpause()
    time.sleep(2)
    logger.debug('stop')
    c.stop()
    c.play(filename)
    time.sleep(3)
    c.play(filename)

if __name__ == '__main__':
    main()
