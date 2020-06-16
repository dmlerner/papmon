#!/usr/bin/sh
here=$(dirname $(realpath $0))
rm -f $here/*.err
node poll-plug.js 2> $here/poll.err &
python3 -m papmonitor 2> $here/papmonitor.err &
