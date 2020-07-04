#!/usr/bin/sh
# TODO: make sure chromecast stfus
pgrep node.*poll-plug.js -f | xargs kill -9 2> /dev/null || echo > /dev/null
pgrep python3.*papmonitor -f | xargs kill -9 2> /dev/null || echo > /dev/null
