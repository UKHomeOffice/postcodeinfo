#!/bin/bash
#
# General-purpose offline table import functions
# Calling run_import() will import any csv file to any table, 
# PROVIDED THAT:
#
#   1) Your calling script defines these env vars:
#       OFFLINE_TABLE_NAME (e.g. 'postcode_api_address_offline')
#       PREV_LIVE_TABLE_NAME (e.g. 'postcode_api_address_prev_live')
#       TEMP_TABLE_NAME (e.g. 'tmp_addressbase_import')
#       LIVE_TABLE_NAME (e.g. 'postcode_api_address')
#       HEADER ('HEADER' if your csv file has a header row, else blank)
#
#   2) Your calling script defines these functions:
#       create_tmp_table_sql
#         - must create a table called $TEMP_TABLE_NAME 
#           with columns defined in the same order
#           as they will appear in the import csv
#       convert_data_sql
#         - take the data in TEMP_TABLE_NAME and insert it into 
#           OFFLINE_TABLE_NAME, performing any transformations 
#           required


function exec_sql {
  echo "$1" | PGPASSWORD=${DB_PASSWORD} psql -q -t -U ${DB_USERNAME} -h ${DB_HOST} -d ${DB_NAME}
}

function exec_in_transaction {
  echo "$1" | PGPASSWORD=${DB_PASSWORD} psql -q -t --single-transaction -U ${DB_USERNAME} -h ${DB_HOST} -d ${DB_NAME}
}

function import_file {
  sql="\COPY $TEMP_TABLE_NAME FROM '$1' WITH CSV $HEADER"
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
  | sed 's/.*INDEX \([^ ]*\).*/ALTER INDEX \1 RENAME TO Z_\1;/' \
  | sed "s/Z_${2}_/${3}_/"
}

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
  "
}

# actually do the whole process
function run_import {
  echo "creating temporary import table"
  exec_sql "$(create_tmp_table_sql)"

  expected_columns=$(columns_in_table "$TEMP_TABLE_NAME")

  for filename in $@; do
    cols_in_file=$(columns_in_csv $filename)
    if [ "${cols_in_file}" == "${expected_columns}" ]; then
      echo "importing ${filename}"
      import_file $filename
    else
      echo "file ${filename} has ${cols_in_file} columns - expected ${expected_columns} - aborting!"
      exec_sql "DROP TABLE $TEMP_TABLE_NAME;"
      exit 1
    fi
  done

  echo "converting data"
  # NOTE: the rename_indexes_sql must be generated AFTER
  # the cleanup_tables_sql has been run!
  exec_in_transaction "$(convert_data_sql)" && \
   exec_in_transaction "$(cleanup_tables_sql)" && \
   exec_in_transaction "$(rename_indexes_sql $LIVE_TABLE_NAME $OFFLINE_TABLE_NAME $LIVE_TABLE_NAME)"
}

# count the number of columns in a single line of csv
function columns_in_csv {
  echo $(awk -F, 'NR==1 { print NF }' $1)
}

function columns_in_table {
  echo $(exec_sql "select count(column_name) from information_schema.columns where table_name='$1'")
}
