import time
import os
import pychromecast 
import contextlib
import wslprocess

import logging
print(__name__)

class ChromeCast:

    @staticmethod
    def get_by_name(name):
        chromecasts = pychromecast.get_chromecasts()
        print('found chromecasts: %s',
                [c.device.friendly_name for c in chromecasts])
        return next(cc for cc in chromecasts if cc.device.friendly_name == name)

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

    def set_volume(self): # float [0,1]
        return self.get_chromecast().set_volume()

    def status(self):
        return self.get_chromecast().status()

    def get_chromecast(self):
        if self._chromecast is None:
            self._chromecast = ChromeCast.get_by_name(self.name)
        assert self._chromecast
        return self._chromecast

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
                f'--sout-chromecast-ip={self.ip()}',
                #'>logs 2>&1', # TODO: handle logging
                )

    def get_play_command(self, media_path):
        player_path = ChromeCast.get_player_path()
        flags = self.get_play_flags()
        return f'{player_path} {" ".join(flags)} {media_path} &'

    def play(self, media_path):
        print('play %s', media_path)
        command = self.get_play_command(media_path)

        self._chromecast.wait() # TODO: needed? move to init?
        # print(self._chromecast.status)
        # print(self._chromecast.device)
        # mc = self._chromecast.media_controller
        # print(mc.status)

        # Needed to avoid connection noise
        print('muting')
        self.mute()
        time.sleep(5)
        print(command)
        existing_vlcs = wslprocess.get_pids('vlc')
        os.system(command)
        time.sleep(5)
        self.vlc_pid = (wslprocess.get_pids('vlc') - existing_vlcs).pop()
        print('unmuting')
        self.unmute()
    
    def stop(self):
        print('')
        self._chromecast.media_controller.stop()

    def unpause(self):
        print('')
        self._chromecast.media_controller.play()

    def close(self):
        print('')
        self.stop()
        self._chromecast.disconnect()
        wslprocess.kill_pids([self.vlc_pid])

    def is_open(self):
        return self.vlc_pid in wslprocess.getpids('vlc')


def main():
    global c, cc, mc
    with contextlib.closing(ChromeCast('bedroom speaker')) as c:
        cc = c.get_chromecast()
        mc = cc.media_controller
        #c = ChromeCast('Gym')
        print('play')
        filename = 'file:///C:/Users/david/google-drive/coding/papmonitor/papmonitor/alarm/audio.mp3'
        #import pdb; pdb.set_trace()

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
