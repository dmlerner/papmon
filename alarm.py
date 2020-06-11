from utils import *
import os

def play_audio_alarm():
    debug('play_audio_alarm')
    vlc = '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'
    filename = '_poet.mp3'
    debug('let"s not actually play that seems annoying')
    return
    os.system(vlc + ' ' + filename)

