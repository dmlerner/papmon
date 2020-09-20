#!/usr/bin/sh
# must run from papmonitor because inner folder name matches outer; change outer TODO
dt="${1:-10}"
cmd="python3 -m papmonitor --snooze $dt"
echo $cmd
$cmd
