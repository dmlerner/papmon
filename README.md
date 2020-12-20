This sets off an alarm if you remove your cpap mask, by monitoring a Kasa HS110 smart plug/power meter.
It is designed to be left running. The alarm will go off if it is nighttime hours, and you have worn the mask for at least a few minutes, and you take it off for at least a few minutes.

Installation instructions:

Good luck with that. Hopefully I'll get this on PIP or something. Requires Javascript (to talk to the plug) and Python (for the bulk of the logic). A number of scripts exist under management-scripts to start it up.

The alarm is played with a hard-coded mp3 file, included in the repo. This has some hard coded paths I need to make into parameters, including for VLC, which is used to chromecast the alarm to my Google Home.

Configurable in papmonitor/\_\_main\_\_.py. 
