#!/bin/bash
VIRTUALENV=var
test -d "$VIRTUALENV" || virtualenv --distribute --no-site-packages "$VIRTUALENV"
. "$VIRTUALENV/bin/activate"
python setup.py install
twistd -n cardshuffle -n 3 &
sleep 1.5
echo -e "random\nready" | nc localhost 1030 >/dev/null &
echo -e "random\nready" | nc localhost 1030 >/dev/null &
nc localhost 1030
sleep 0.5
kill %1 %2 %3
