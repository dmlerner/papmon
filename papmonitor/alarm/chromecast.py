import time
import os
import pychromecast 

def get_chromecast(name):
    chromecasts = pychromecast.get_chromecasts()
    #print(c.device.friendly_name for c in chromecasts)
    return next(cc for cc in chromecasts if cc.device.friendly_name == name)

def get_vlc_command(cast_ip, media_path):
    executable = '/mnt/c/Program\ Files/VideoLAN/VLC/vlc.exe'
    flags = (
            '-I dummy --dummy-quiet',
            '--play-and-exit',
            '--sout="#chromecast"',
            '--demux-filter=demux_chromecast',
            f'--sout-chromecast-ip={cast_ip}',
            #'>/dev/null 2>&1',
            )

    return f'{executable} {" ".join(flags)} {media_path} &'


    # --play-and-exit  --sout-chromecast-ip=192.168.1.19 --sout="#chromecast" audio.mp3  --demux-filter=demux_chromecast &
cc = get_chromecast('Gym')
cc.wait()
print(cc.status)
print(cc.device)
mc = cc.media_controller
print(mc.status)
ip = cc.host
cmd = get_vlc_command(ip, 'audio.mp3')
f=lambda: os.system(cmd)
cc.set_volume_muted(True)
#input('press a key to run cmd')
time.sleep(5)
print(cmd)
os.system(cmd)
time.sleep(5)
#input('press a key to unmute')
print('unmuting')
cc.set_volume_muted(False)

#time.sleep(2)
#os.system(cmd)
# Start worker thread and wait for cast device to be ready
#cast.wait()
#print(cast.device)# DeviceStatus(friendly_name='Living Room', model_name='Chromecast', manufacturer='Google Inc.', uuid=UUID('df6944da-f016-4cb8-97d0-3da2ccaa380b'), cast_type='cast') 
#print(cast.status)# CastStatus(is_active_input=True, is_stand_by=False, volume_level=1.0, volume_muted=False, app_id='CC1AD845', display_name='Default Media Receiver', namespaces=['urn:x-cast:com.google.cast.player.message', 'urn:x-cast:com.google.cast.media'], session_id='CCA39713-9A4F-34A6-A8BF-5D97BE7ECA5C', transport_id='web-9', status_text='') 
#mc = cast.media_controller
#mc.play_media('http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'video/mp4')
#mc.play_media('/mnt/c/Users/david/google-drive/hass-pychromecast/audioooo.mp3', 'audio/mp3')
#mc.play_media('http://192.168.1.36:8000/audio.mp3', 'audio/mp3')
#mc.play_media('http://0.0.0.0:8000/mnt/c/Users/david/google-drive/coding/hass-pychromecast/audio.mp3', 'audio/mp3')
#mc.play_media('http://0.0.0.0:8000/BigBuckBunny.mp4', 'video/mp4')
#print(mc.status) # MediaStatus(current_time=42.458322, content_id='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', content_type='video/mp4', duration=596.474195, stream_type='BUFFERED', idle_reason=None, media_session_id=1, playback_rate=1, player_state='PLAYING', supported_media_commands=15, volume_level=1, volume_muted=False) 
#mc.pause()
#time.sleep(5)
#mc.volume_muted = True
#print(mc.status) # MediaStatus(current_time=42.458322, content_id='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', content_type='video/mp4', duration=596.474195, stream_type='BUFFERED', idle_reason=None, media_session_id=1, playback_rate=1, player_state='PLAYING', supported_media_commands=15, volume_level=1, volume_muted=False) 
#time.sleep(3)
#mc.stop()
#mc.volume_muted = True
#print(mc.status) # MediaStatus(current_time=42.458322, content_id='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', content_type='video/mp4', duration=596.474195, stream_type='BUFFERED', idle_reason=None, media_session_id=1, playback_rate=1, player_state='PLAYING', supported_media_commands=15, volume_level=1, volume_muted=False) 
#mc.play()
#print(r)
#input('playing, enter to quit')

'''
python mutes speaker
vlc plays alarm music
python unmutes speaker
python mutes speaker
python plays silence

to quit vlc, just play a short silent track with the and exit flag
    works
even just having a pychromecast connection open means no connection noise, even from vlc!
'''
