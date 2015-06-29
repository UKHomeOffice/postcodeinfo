#!/bin/bash

echo "*******************************************"
echo "AddressBase Basic"
BATCH_IMPORT_NUM_ROWS=100000 BULK_CREATE_BATCH_SIZE=5000 ./manage.py download_and_import_addressbase_basic

echo "*******************************************"
echo "Local Authorities"
./manage.py download_and_import_local_authorities

echo "*******************************************"
echo "Postcode / GSS Codes"
./manage.py download_and_import_postcode_gss_codes
