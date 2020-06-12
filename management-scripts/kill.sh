#1/usr/bin/bash
pgrep node.*poll-plug.js -f | xargs kill -9 2&>/dev/null
pgrep python3.*papmonitor -f | xargs kill -9 2&>/dev/null
