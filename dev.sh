#!/bin/bash
UNIQ_VER=$(date +%s)

# Run postgis
docker run --name postcode-db-$UNIQ_VER -e POSTGRES_PASSWORD=postcodeinfo -e POSTGRES_USER=postcodeinfo -d mdillon/postgis:9.3

# Run postcodeinfo and link it to postgis
docker build -t postcodeinfo-dev .
docker run -p 8000:80 --name postcode-web-$UNIQ_VER --link postcode-db-$UNIQ_VER:postgres -e DB_PASSWORD=postcodeinfo -e DB_USER=postcodeinfo -d postcodeinfo-dev

#docker rm -f postcode-db-$UNIQ_VER
#docker rm -f postcode-web-$UNIQ_VER

