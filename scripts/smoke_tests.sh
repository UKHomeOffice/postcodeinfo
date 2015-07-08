#!/bin/bash -e

# Run some simple tests against a genuine API instance
# Useful for running after a deploy
# Requires two env variables:
# API_AUTH_TOKEN (a valid token from the target service)
# API_ROOT_URL (e.g. https://postcodeinfo-staging.dsd.io/) 

echo "Running smoke tests against ${API_ROOT_URL}"
./manage.py test postcodeinfo/apps/postcode_api/smoke_tests/ --testrunner=postcode_api.smoke_tests.no_db_test_runner.NoDbTestRunner

