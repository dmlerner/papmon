import time
import os
import pychromecast 
import contextlib

import logging
logger = logging.getLogger(__name__)

class ChromeCast:

    @staticmethod
    def or_reset(f):
        def _f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                self._chromecast = None
        return _f

    def __init__(self, name):
        self.name = name
        self._chromecast = Chromecast.get_by_name(name)
        self.ip = self._chromecast.host
        self.pause = self._chromecast.media_controller.pause
        self.set_volume_muted = self._chromecast.set_volume_muted
        self.set_volume = self._chromecast.set_volume
        self.status = self._chromecast.status

    def get_chromecast(self):
        if self._chromecast is None:
            self._chromecast = ChromeCast.get_by_name(self.chromecast_name)
        return self._chromecast

    @staticmethod
    def get_by_name(name):
        chromecasts = pychromecast.get_chromecasts()
        logger.debug('found chromecasts: %s',
                [c.device.friendly_name for c in chromecasts])
        return next(cc for cc in chromecasts if cc.device.friendly_name == name)

    @staticmethod
    def get_player_path():
        # Underlying pychromecast.Chromecast.play_media expects a url
        # And I can't make it work with local media
        # Even with eg Python's http.server
        return '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'

    def get_play_flags(self):
        return ( 
                #'-I dummy --dummy-quiet', # no gui
                '--play-and-exit',
                '--sout="#chromecast"',
                '--demux-filter=demux_chromecast',
                f'--sout-chromecast-ip={self.ip}',
                #'>logs 2>&1', # TODO: handle logging
                )

    def get_play_command(self, media_path):
        player_path = ChromeCast.get_player_path()
        flags = self.get_play_flags()
        return f'{player_path} {" ".join(flags)} {media_path} &'

    @or_reset
    def play(self, media_path):
        logger.info('play %s', media_path)
        command = self.get_play_command(media_path)

        self._chromecast.wait() # TODO: needed? move to init?
        # print(self._chromecast.status)
        # print(self._chromecast.device)
        # mc = self._chromecast.media_controller
        # print(mc.status)

        # Needed to avoid connection noise
        logger.debug('muting')
        self.set_volume_muted(True)
        time.sleep(5)
        logger.info(command)
        os.system(command)
        time.sleep(5)
        logger.debug('unmuting')
        self.set_volume_muted(False)
    
    @or_reset
    def stop(self):
        logger.info('')
        self._chromecast.media_controller.stop()

    @or_reset
    def unpause(self):
        logger.info('')
        self._chromecast.media_controller.play()

    @or_reset
    def close(self):
        logger.info('')
        self.stop()
        self._chromecast.disconnect()


def main():
    global c, cc, mc
    with contextlib.closing(ChromeCast('bedroom speaker')) as c:
        cc = c._chromecast
        mc = cc.media_controller
        #c = ChromeCast('Gym')
        print('play')
        filename = 'file:///C:/Users/david/google-drive/coding/papmonitor/papmonitor/alarm/audio.mp3'
        c.play(filename)
        print('pause')
        c.pause()
        time.sleep(2)
        print('unpause')
        c.unpause()
        time.sleep(2)
        print('stop')
        c.stop()

if __name__ == '__main__':
    main()
