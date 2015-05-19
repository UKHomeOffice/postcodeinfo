#!/bin/bash

# jenkins fires up the db docker container in the background and exits
# immediately, then runs this - so the db may not be ready.
wait_for() {
    while ! curl http://$1:$2/
    do
        echo "Waiting for $1 ..."
        sleep 1
    done
}

wait_for $DB_HOST $DB_PORT

rm -f htmlcov/*
rm -f .coverage

coverage run --source='.' ./manage.py test

PARMS=--omit='*migrations*'
echo "Coverage results:"
coverage report $PARMS
coverage html $PARMS
echo "HTML report generated in htmlcov/index.html"
