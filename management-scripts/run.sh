#!/usr/bin/sh
rm -f *.err
node poll-plug.js 2> ./management-scripts/poll.err &
python3 -m papmonitor 2> ./management-scripts/papmonitor.err &
