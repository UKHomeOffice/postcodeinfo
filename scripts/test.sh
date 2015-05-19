#!/bin/bash

rm -f htmlcov/*
rm -f .coverage

coverage run --source='.' ./manage.py test

PARMS=--omit='*migrations*'
echo "Coverage results:"
coverage report $PARMS
coverage html $PARMS
echo "HTML report generated in htmlcov/index.html"
