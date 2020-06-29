import time
import os
import pychromecast 
import contextlib

import logging
logger = logging.getLogger(__name__)

class ChromeCast:
    def __init__(self, name):
        self._chromecast = ChromeCast.get(name)
        self.ip = self._chromecast.host
        self.pause = self._chromecast.media_controller.pause
        self.set_volume_muted = self._chromecast.set_volume_muted
        self.set_volume = self._chromecast.set_volume
        self.status = self._chromecast.status

    @staticmethod
    def get(name):
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
    
    def stop(self):
        logger.info('')
        self._chromecast.media_controller.stop()

    def unpause(self):
        logger.info('')
        self._chromecast.media_controller.play()

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
        c.play('audio.mp3')
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
