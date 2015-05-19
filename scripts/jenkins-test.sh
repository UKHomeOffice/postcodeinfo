#!/bin/bash

# jenkins fires up the db docker container in the background and exits
# immediately and runs the tests, so the db may not be ready.

wait_for() {
    while ! curl http://$1:$2/
    do
        echo "Waiting for $1 ..."
        sleep 1
    done
}

wait_for $DB_HOST $DB_PORT

scripts/test.sh
