#!/bin/bash
VIRTUALENV=var
test -d "$VIRTUALENV" || virtualenv --distribute --no-site-packages "$VIRTUALENV"
. "$VIRTUALENV/bin/activate"
python setup.py install
echo "Launching server.."
twistd -n cardshuffle --players=3 &
sleep 1.5 # wait for the server to start up
echo -e "random\nready" | nc localhost 1030 >/dev/null &
echo -e "random\nready" | nc localhost 1030 >/dev/null &
echo "Connecting.."
nc localhost 1030 # run until human player disconnects
echo "Shutting down.."
sleep 0.5 # wait for the server to tear down
kill %1 %2 %3
