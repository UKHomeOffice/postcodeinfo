#!/bin/bash
#
#The script will:
#  pull down a postgresql + postgis container and run it
#  build a container for the django code, based on the Dockerfile in the repo (so it resembles prod)
#  link the containers
#  runs a django migrate
#  mount the work dir inside the container so one can use his favourite IDE to change code that's running inside the container
#
#Note: django will pick up on the code changes and restart itself automatically


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

django_manage() {
  printf $GREEN "Running ./manage.py $1"
  docker rm postcode-web 2>/dev/null || :
  docker run --rm -ti -p 8000:8000 -v $(pwd):/srv/postcodeinfo \
      --name postcode-web \
      --link postcode-db:postgres \
      -e "DB_PASSWORD=postcodeinfo" \
      -e "DB_USER=postcodeinfo" \
      -e "OS_FTP_USERNAME=${OS_FTP_USERNAME:-anonymous}" \
      -e "OS_FTP_PASSWORD=${OS_FTP_PASSWORD:-anonymous@}" \
      -e "DJANGO_DEBUG=${DJANGO_DEBUG:-True}" \
      -e "DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS:-}" \
      -e "DB_NAME=postcodeinfo" \
      -e "DB_USERNAME=postcodeinfo" \
      -e "DB_PASSWORD=postcodeinfo" \
      -e "DB_HOST=postgres" \
      -e "DB_PORT=5432" \
      postcodeinfo-dev ./manage.py $1
}

printf $GREEN "Looking for an existing postgis container..."
docker inspect postcode-db|grep '"Running": true' 2>&1>/dev/null || run_postgis_container

# Give the postgis container a chance to start
sleep 5

build_django_app_container || printf $RED "Failed to build container"

django_manage "migrate" || printf $RED "Failed to execute django migration"
django_manage "collectstatic --noinput" || printf $RED "Failed to execute django collectstatic"
django_manage "runserver 0.0.0.0:8000"
