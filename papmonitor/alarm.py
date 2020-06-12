import os

import logging
logger = logging.getLogger(__name__)

def play_audio_alarm():
    logger.debug('play_audio_alarm')
    vlc = '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'
    filename = '_poet.mp3'
    logger.debug('let"s not actually play that seems annoying')
    os.system(vlc + ' ' + filename)
    return

