 lsof | ag node.*poll.out | head -n 1 | sed -e 's/node *//' | sed -e 's/ .*//' | xargs kill -9
