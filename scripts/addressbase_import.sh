#!/bin/bash

OFFLINE_TABLE_NAME='postcode_api_address_offline'
PREV_LIVE_TABLE_NAME='postcode_api_address_prev_live'
TEMP_TABLE_NAME='tmp_addressbase_import'
LIVE_TABLE_NAME='postcode_api_address'

function exec_sql {
  echo "$1" | PGPASSWORD=${DB_PASSWORD} psql -q -t -U ${DB_USERNAME} -h ${DB_HOST} -d ${DB_NAME}
}

function exec_in_transaction {
  echo "$1" | PGPASSWORD=${DB_PASSWORD} psql -q -t --single-transaction -U ${DB_USERNAME} -h ${DB_HOST} -d ${DB_NAME}
}

function import_file {
  sql="\COPY $TEMP_TABLE_NAME FROM '$1' WITH CSV"
  # restore this line if you need to mix a \copy command in with
  # other sql statements in the same execution, as it needs to be
  # terminated with a newline and a double backslash
  #sql=$sql$'\n'"\\\\"$'\n'
  exec_sql "$sql"
}

function copy_indexes_sql {
  exec_sql "select indexdef from pg_indexes where tablename = '$LIVE_TABLE_NAME'" \
  | sed 's/CREATE INDEX .* ON /CREATE INDEX ON /g' \
  | sed 's/CREATE UNIQUE INDEX .* ON /CREATE UNIQUE INDEX ON /g' \
  | sed "s/$LIVE_TABLE_NAME/$OFFLINE_TABLE_NAME/g" \
  | sed 's/$/;/' \
  | sed 's/^;//'
}

# args: 
#   table name on which indexes will be renamed
#   table name to replace in index names
#   table name to substitute into index names
function rename_indexes_sql {
  exec_sql "select indexdef from pg_indexes where tablename = '$1'" \
  | sed 's/.*INDEX \([^ ]*\).*/ALTER INDEX \1 RENAME TO ZZZ_\1;/' \
  | sed "s/ZZZ_${2}_/${3}_/"
}

# read -d'' reads multiple lines from stdin ignoring newlines
# see http://serverfault.com/a/72511 for more details of how this works
CREATE_TABLE_SQL="
  DROP TABLE IF EXISTS $TEMP_TABLE_NAME;

  -- UPRN is unquoted in the import, hence it has to be a bigint here
  CREATE UNLOGGED TABLE $TEMP_TABLE_NAME ( 
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

  TRUNCATE TABLE $TEMP_TABLE_NAME;
"


# yes, get rid of any address named in the import, regardless of change type
# as for an insert or update, we can just delete and (re-)insert
CONVERT_DATA_SQL="
  DROP TABLE IF EXISTS $OFFLINE_TABLE_NAME;

  SELECT 'creating offline table' AS status;
  CREATE TABLE $OFFLINE_TABLE_NAME AS 
    SELECT * from $LIVE_TABLE_NAME WHERE uprn NOT IN (
      SELECT cast(UPRN AS varchar(12)) from $TEMP_TABLE_NAME WHERE CHANGE_TYPE='D'
    );

  SELECT 'removing uprns seen in the import from offline table' AS status;
  DELETE FROM $OFFLINE_TABLE_NAME WHERE uprn IN (
    SELECT cast(UPRN AS varchar(12)) FROM $TEMP_TABLE_NAME
  );

  SELECT 'converting import data into offline address table' AS status;
  INSERT INTO $OFFLINE_TABLE_NAME
  (
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
  FROM $TEMP_TABLE_NAME;

  TRUNCATE TABLE $TEMP_TABLE_NAME;
"


function cleanup_tables_sql {
  echo "
    SELECT 'removing tmp import table' AS status;
    DROP TABLE $TEMP_TABLE_NAME;

    SELECT 'copying indexes onto offline table' AS status;
    `copy_indexes_sql`

    SELECT 'renaming tables' AS status;
    SELECT 'dropping $PREV_LIVE_TABLE_NAME' AS status;
    DROP TABLE IF EXISTS $PREV_LIVE_TABLE_NAME;
    SELECT 'renaming $LIVE_TABLE_NAME to $PREV_LIVE_TABLE_NAME' AS status;
    ALTER TABLE $LIVE_TABLE_NAME RENAME TO $PREV_LIVE_TABLE_NAME;
    $(rename_indexes_sql $LIVE_TABLE_NAME $LIVE_TABLE_NAME $PREV_LIVE_TABLE_NAME)

    SELECT 'renaming $OFFLINE_TABLE_NAME to $LIVE_TABLE_NAME' AS status;
    ALTER TABLE $OFFLINE_TABLE_NAME RENAME TO $LIVE_TABLE_NAME;
    $(rename_indexes_sql $OFFLINE_TABLE_NAME $OFFLINE_TABLE_NAME $LIVE_TABLE_NAME)
  "
}


if [ $# -eq 0 ]
  then 
    echo "No arguments supplied"
    exit 1
else
  echo "creating temporary import table"
  exec_sql "$CREATE_TABLE_SQL"

  for filename in $@; do
    echo "importing ${filename}"
    import_file $filename
  done

  exec_sql "SELECT CHANGE_TYPE, COUNT(*) AS num_to_import FROM $TEMP_TABLE_NAME GROUP BY CHANGE_TYPE;"
  echo "converting data"
  exec_in_transaction "$CONVERT_DATA_SQL" && \
    exec_in_transaction "$(cleanup_tables_sql)"
fi
  


