#!/bin/bash

function exec_sql {
  echo "$1" | PGPASSWORD=${DB_PASSWORD} psql -q -t -U ${DB_USERNAME} -h ${DB_HOST} -d ${DB_NAME}
}

function exec_in_transaction {
  echo "$1" | PGPASSWORD=${DB_PASSWORD} psql -q -t --single-transaction -U ${DB_USERNAME} -h ${DB_HOST} -d ${DB_NAME}
}

function import_file {
  sql="\COPY tmp_addressbase_import FROM '$1' WITH CSV"
  # restore this line if you need to mix a \copy command in with
  # other sql statements in the same execution, as it needs to be
  # terminated with a newline and a double backslash
  #sql=$sql$'\n'"\\\\"$'\n'
  exec_sql "$sql"
}

# read -d'' reads multiple lines from stdin ignoring newlines
# see http://serverfault.com/a/72511 for more details of how this works
read -d '' CREATE_TABLE_SQL <<"EOF"
  DROP TABLE IF EXISTS tmp_addressbase_import;

  -- UPRN is unquoted in the import, hence it has to be a bigint here
  CREATE UNLOGGED TABLE tmp_addressbase_import ( 
    UPRN bigint, 
    OS_ADDRESS_TOID varchar(40), 
    RM_UDPRN integer, 
    ORGANISATION_NAME varchar(120), 
    DEPARTMENT_NAME varchar(120), 
    PO_BOX_NUMBER varchar(12), 
    BUILDING_NAME varchar(100), 
    SUB_BUILDING_NAME varchar(60), 
    BUILDING_NUMBER integer, 
    DEPENDENT_THOROUGHFARE_NAME varchar(160), 
    THOROUGHFARE_NAME varchar(160), 
    POST_TOWN varchar(60), 
    DOUBLE_DEPENDENT_LOCALITY varchar(70), 
    DEPENDENT_LOCALITY varchar(70), 
    POSTCODE varchar(16), 
    POSTCODE_TYPE char(2), 
    X_COORDINATE float, 
    Y_COORDINATE float, 
    RPC integer, 
    CHANGE_TYPE char(2), 
    START_DATE date, 
    LAST_UPDATE_DATE date, 
    ENTRY_DATE date, 
    CLASS char(2), 
    PROCESS_DATE date
  );

  TRUNCATE TABLE tmp_addressbase_import;
EOF


# yes, get rid of any address named in the import, regardless of change type
# as for an insert or update, we can just delete and (re-)insert
read -d '' CONVERT_DATA_SQL <<"EOF"
  SELECT 'removing any existing addresses with UPRNs in the import file' AS status;
  DELETE FROM postcode_api_address USING tmp_addressbase_import
    WHERE postcode_api_address.uprn = cast(tmp_addressbase_import.UPRN AS varchar(12));

  SELECT 'removing any change_type "D" import records' AS status;
  DELETE FROM tmp_addressbase_import WHERE CHANGE_TYPE = 'D';

  SELECT 'converting import data into live address table' AS status;
  INSERT INTO postcode_api_address (
    uprn,
    os_address_toid,
    rm_udprn,
    organisation_name,
    department_name,
    po_box_number,
    building_name,
    sub_building_name,
    building_number,
    dependent_thoroughfare_name,
    thoroughfare_name,
    post_town,
    double_dependent_locality,
    dependent_locality,
    point,
    postcode,
    postcode_index,
    postcode_type,
    rpc,
    change_type,
    start_date,
    last_update_date,
    entry_date,
    primary_class,
    process_date,
    postcode_area
  ) SELECT 
    cast(UPRN AS varchar(12)),
    OS_ADDRESS_TOID, 
    RM_UDPRN, 
    ORGANISATION_NAME, 
    DEPARTMENT_NAME, 
    COALESCE(PO_BOX_NUMBER, ''), 
    BUILDING_NAME, 
    SUB_BUILDING_NAME, 
    BUILDING_NUMBER, 
    DEPENDENT_THOROUGHFARE_NAME, 
    THOROUGHFARE_NAME, 
    POST_TOWN, 
    DOUBLE_DEPENDENT_LOCALITY, 
    DEPENDENT_LOCALITY, 
    st_transform(ST_GeomFromText('POINT('||X_COORDINATE||' '||Y_COORDINATE||')',27700),4326),
    POSTCODE, 
    lower(regexp_replace(POSTCODE, ' ', '')),
    POSTCODE_TYPE, 
    RPC, 
    CHANGE_TYPE, 
    START_DATE, 
    LAST_UPDATE_DATE, 
    ENTRY_DATE, 
    CLASS, 
    PROCESS_DATE,
    lower(split_part(POSTCODE, ' ', 1))
  FROM tmp_addressbase_import;

  TRUNCATE TABLE tmp_addressbase_import;
EOF

read -d '' CLEANUP_SQL <<"EOF"
  SELECT 'removing tmp import table' AS status;
  DROP TABLE tmp_addressbase_import;
EOF


echo "creating temporary import table"
exec_sql "$CREATE_TABLE_SQL"

for filename in $@; do

  echo "importing ${filename}"
  import_file $filename
  
done

exec_sql "SELECT CHANGE_TYPE, COUNT(*) AS num_to_import FROM tmp_addressbase_import GROUP BY CHANGE_TYPE;"
echo "converting data"
exec_in_transaction "$CONVERT_DATA_SQL"
exec_sql "$CLEANUP_SQL"
