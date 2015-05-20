#!/bin/bash

# jenkins fires up the db docker container in the background and exits
# immediately and runs the tests, so the db may not be ready.

max_tries=60

ready=0
tries=0

db_ready() {
    echo "Waiting for $DB_HOST ... "
    tries=$((tries + 1))
    pg_isready -h $DB_HOST -p $DB_PORT &>/dev/null
    ready=$?
    return $ready
}

while ! db_ready
do
    if [ $tries -gt $max_tries ]; then
        break
    fi
    sleep 1
done

if [ $ready -ne 0 ]; then
    echo "Gave up"
    exit 1
fi

scripts/test.sh
