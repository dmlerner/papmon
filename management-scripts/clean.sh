#!/usr/bin/sh
here=$(dirname $(realpath $0))
root=$(dirname $here)
rm -f $root/data/power/* $root/papmonitor/logs/*
