#!/usr/bin/sh
# TODO: make sure chromecast stfus
python3 -m papmonitor --kill
pgrep node.*poll-plug.js -f | xargs kill -9 2> /dev/null || echo > /dev/null
pgrep python3.*papmonitor -f | xargs kill -9 2> /dev/null || echo > /dev/null
