#!/usr/bin/sh
mv ../data/power/* old
node poll-plug.js 2> poll.err &
python3 -m papmonitor 2> papmonitor.err &
