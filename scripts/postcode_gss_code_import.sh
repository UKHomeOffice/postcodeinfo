#!/bin/bash -e

OFFLINE_TABLE_NAME='postcode_api_postcodegsscode_offline'
PREV_LIVE_TABLE_NAME='postcode_api_postcodegsscode_prev_live'
TEMP_TABLE_NAME='tmp_postcodegsscode_import'
LIVE_TABLE_NAME='postcode_api_postcodegsscode'
HEADER=' HEADER '

#: EPSG projection codes
BRITISH_NATIONAL_GRID=27700
WGS84=4326

# bring in general-purpose functions
source `dirname $0`/offline_table_import_functions.sh

function create_tmp_table_sql {
  echo "
    DROP TABLE IF EXISTS $TEMP_TABLE_NAME;

    -- UPRN is unquoted in the import, hence it has to be a bigint here
    CREATE UNLOGGED TABLE $TEMP_TABLE_NAME ( 
      pcd char(7),
      pcd2 char(8),
      pcds char(8),
      dointr char(6),
      doterm char(6),
      usertype char(8),
      oseast1m char(6),
      osnrth1m char(7),
      osgrdind char,
      oa01 char(10),
      cty varchar(10),
      laua varchar(10),
      ward varchar(10),
      hlthau varchar(10),
      hro varchar(10),
      ctry varchar(10),
      gor varchar(10),
      pcon varchar(10),
      eer varchar(10),
      teclec varchar(10),
      ttwa varchar(10),
      pct varchar(10),
      nuts varchar(10),
      park varchar(10),
      lsoa01 varchar(10),
      msoa01 varchar(10),
      wz11 varchar(10),
      ccg varchar(10),
      bua11 varchar(10),
      buasd11 varchar(10),
      ru11ind char(2),
      oac11 char(3),
      lat float NULL,
      long float NULL,
      lep1 varchar(10),
      lep2 varchar(10),
      pfa varchar(10),
      imd varchar(10)
  );
  "
}


# yes, get rid of any address named in the import, regardless of change type
# as for an insert or update, we can just delete and (re-)insert
function convert_data_sql {
  echo "
    DROP TABLE IF EXISTS $OFFLINE_TABLE_NAME;

    SELECT 'creating offline table' AS status;
    CREATE TABLE $OFFLINE_TABLE_NAME AS 
      SELECT * from $LIVE_TABLE_NAME LIMIT 1;

    SELECT 'truncating offline table' AS status;
    TRUNCATE $OFFLINE_TABLE_NAME;

    SELECT 'converting import data into offline table' AS status;
    INSERT INTO $OFFLINE_TABLE_NAME
    (
      postcode_index,
      local_authority_gss_code,
      country_gss_code
    ) SELECT 
      lower(regexp_replace(PCD, ' +', '')),
      laua, 
      ctry
    FROM $TEMP_TABLE_NAME;

    TRUNCATE TABLE $TEMP_TABLE_NAME;
  "
}




# Main processing actually starts here
if [ $# -eq 0 ]
  then 
    echo "No arguments supplied"
    exit 1
else
  run_import "$@"
fi



