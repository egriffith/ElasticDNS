#! /bin/sh

set -e
trap exit_script 1 2 3 6

exit_script() {
    echo "Caught Signal ... cleaning up."
    trap - SIGINT SIGTERM # clear the trap
    kill -- -$$ # Sends SIGTERM to child/sub processes
}

while true
do
    /app/elasticdns.py $@
    sleep 300 &
    wait %1
done