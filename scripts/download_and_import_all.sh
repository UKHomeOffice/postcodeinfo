#!/bin/bash

echo "*******************************************"
echo "AddressBase Basic"
./manage.py download_and_import_addressbase_basic

echo "*******************************************"
echo "Local Authorities"
./manage.py download_and_import_local_authorities

echo "*******************************************"
echo "Postcode / GSS Codes"
./manage.py download_and_import_postcode_gss_codes
