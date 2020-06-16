#!/usr/bin/sh
here=$(dirname $(realpath $0))
sh $here/kill.sh
sh $here/run.sh
