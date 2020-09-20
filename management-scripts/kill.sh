#!/usr/bin/sh
# TODO: make sure chromecast stfus
pgrep node.*poll-plug.js -f | xargs kill -9 2> /dev/null || echo > /dev/null
python3 -m papmonitor --kill
echo 'sleep 5'
sleep 5 # kill uses snooze logic in papmon, let it run a bit
pgrep python3.*papmonitor -f | xargs kill -9 2> /dev/null || echo > /dev/null
