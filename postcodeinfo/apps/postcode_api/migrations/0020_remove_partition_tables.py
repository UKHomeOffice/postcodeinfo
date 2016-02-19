# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.db import migrations


def drop_trigger_if_exists_sql(trigger_name):
    return """
        DROP TRIGGER IF EXISTS {name} ON postcode_api_address CASCADE;
        """.format(name=trigger_name)

def drop_function_if_exists_sql(function_name):
    return """
        DROP FUNCTION IF EXISTS {name}() CASCADE;
        """.format(name=function_name)

def drop_triggers(apps, schema_editor):
    for name in ['before_insert_postcode_api_address_trigger', 'after_insert_postcode_api_address_trigger']:
        schema_editor.execute(drop_trigger_if_exists_sql(name))

def drop_functions(apps, schema_editor):
    for name in ['postcode_api_address_insert_child', 'postcode_api_address_delete_master']:
        schema_editor.execute(drop_function_if_exists_sql(name))

def un_partition_address_table(apps, schema_editor):
    all_possible_prefixes = string.ascii_lowercase + string.digits
    for first_char in all_possible_prefixes:
        sql = """
            DO $$
            BEGIN
            IF EXISTS(SELECT * FROM information_schema.tables WHERE table_name = 'postcode_api_address_{suffix}')
            THEN 
                INSERT INTO postcode_api_address
                SELECT * FROM postcode_api_address_{suffix};

                DROP TABLE postcode_api_address_{suffix};
            END IF;
            END $$;
        """.format(suffix=first_char)
        print("insert-selecting into live address table"
              " from partition {char}").format(char=first_char)
        schema_editor.execute(
            sql, ['{first_char}%'.format(first_char=first_char)])

    

class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0019_populate_partition_tables'),
    ]

    operations = [
        migrations.RunPython(un_partition_address_table),
        migrations.RunPython(drop_triggers),
        migrations.RunPython(drop_functions),
    ]
