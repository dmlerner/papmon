from utils import *

playing = False
def play_audio_alarm():
    debug('play_audio_alarm')
    if playing:
        return
    debug('playing audio alarm')
    vlc = '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'
    filename = 'poet.mp3'
    playing = True
    os.system(vlc + ' ' + filename)

