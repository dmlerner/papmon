#!/usr/bin/sh
echo "running poll"
node poll.js > poll.out 2> poll.err &
echo "running driver"
python3 driver.py > driver.out 2> driver.err &
