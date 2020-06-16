#1/usr/bin/sh
pgrep node.*poll-plug.js -f | xargs kill -9 || echo ''
pgrep python3.*papmonitor -f | xargs kill -9 || echo ''
