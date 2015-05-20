#!/bin/bash
set -eu
GREEN='\n\e[1;32m%-6s\e[m\n'
RED='\n\e[1;31m%-6s\e[m\n'

run_postgis_container() {
  printf $GREEN "Postgis container not found or killed, cleaning up and starting a new one."
  docker rm postcode-db 2>/dev/null || :
  docker run -p 5432:5432 --name postcode-db -e POSTGRES_PASSWORD=postcodeinfo -e POSTGRES_USER=postcodeinfo -d mdillon/postgis:9.3
}

build_django_app_container() {
  printf $GREEN "Building the docker container, this might take a few minutes... " && sleep 2
  docker build -t postcodeinfo-dev .
}

django_migrate() {
  printf $GREEN "Running the django migration script"
  docker rm postcode-web 2>/dev/null || :
  docker run --rm -ti -p 8000:8000 -v $(pwd):/srv/postcodeinfo --name postcode-web --link postcode-db:postgres -e DB_PASSWORD=postcodeinfo -e DB_USER=postcodeinfo postcodeinfo-dev ./manage.py migrate
}

django_runserver() {
  printf $GREEN "Running the django container and linking it with the database"
  docker rm postcode-web 2>/dev/null || :
  docker run --rm -ti -p 8000:8000 -v $(pwd):/srv/postcodeinfo --name postcode-web --link postcode-db:postgres -e DB_PASSWORD=postcodeinfo -e DB_USER=postcodeinfo postcodeinfo-dev ./manage.py runserver 0.0.0.0:8000
}

printf $GREEN "Looking for an existing postgis container..."
docker inspect postcode-db|grep '"Running": true' 2>&1>/dev/null || run_postgis_container

# Give the postgis container a chance to start
sleep 5

build_django_app_container || printf $RED "Failed to build container"
django_migrate || printf $RED "Failed to execute django migration"
django_runserver

