#!/usr/bin/sh
node poll.js 2> poll.err &
python3 -m papmonitor 2> papmonitor.err &
