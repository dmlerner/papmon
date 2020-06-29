import os
import glob

import logging
import threading
logger = logging.getLogger(__name__)

#playing = False
last_play = None

import datetime

def play_audio_alarm():
    logger.debug('play_audio_alarm')
    # TODO: logic to kill it, and move logic like this to papmonitor
    global last_play
    if last_play and (datetime.datetime.now() - last_play) < datetime.timedelta(seconds=10):
    #if last_play and (datetime.datetime.now() - last_play) < datetime.timedelta(minutes=5):
        logger.debug('played recently, returning')
        return
    last_play = datetime.datetime.now()
    #global playing
    #if playing:
        #return False
    vlc = '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'
    #filename = '/mnt/c/Users/david/google-drive/coding/papmonitor/data/_poet.mp3'
    #filename = '../data/_poet.mp3'
    #filename = ''
    #filename = 'poop'
    filename = 'file:///C:/Users/david/google-drive/coding/papmonitor/data/_poet.mp3'
    #print(glob.glob(filename.replace('_poet.mp3', '*')))
    command = vlc + ' --play-and-exit ' + filename 
    #command = vlc
    #print(command)
    #kill_audio_alarm()
    logger.info('playing alarm via vlc, command:%s', command)
    #playing = True
    #os.system(command)
    #import time; time.sleep(10)
    #return
    t = threading.Thread(target=lambda:os.system(command))
    t.run()
    #return True


'''
def check_kill():
    while True:
        if should_kill:
            kill_audio_alarm()
            break
def kill_audio_alarm():
    logger.info('killing audio alarm')
    global playing
    playing = False
    return
    #  Close manually for now
    filename = '../data/_poet.mp3'
    try:
        os.system('pgrep "%s" -f | xargs kill -9 2&>/dev/null' % 'poet.mp3')
    except:
        pass

'''

