#1/usr/bin/sh
pgrep node.*poll-plug.js -f | xargs kill -9 2> /dev/null || echo > /dev/null
pgrep python3.*papmonitor -f | xargs kill -9 2> /dev/null || echo > /dev/null
