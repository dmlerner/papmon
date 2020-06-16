#!/usr/bin/sh
here=$(dirname $(realpath $0))
echo 'kill'
$here/kill.sh;
echo 'poll-plug.js'
node $here/../poll-plug.js 2> $here/poll.err &
echo 'python3 -m papmonitor --test'
python3 -m papmonitor --test 2> $here/papmonitor.err &
