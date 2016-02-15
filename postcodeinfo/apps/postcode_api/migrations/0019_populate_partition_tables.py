# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.db import migrations

from postcode_api.models import Address


def partition_address_table(apps, schema_editor):
    Address.architect.partition.get_partition().prepare()

    all_possible_prefixes = string.ascii_lowercase + string.digits
    for first_char in all_possible_prefixes:
        sql = """
            TRUNCATE TABLE postcode_api_address_{suffix};

            INSERT INTO postcode_api_address_{suffix}
            SELECT * FROM postcode_api_address
            WHERE postcode_index LIKE %s;
        """.format(suffix=first_char)
        print "insert-selecting into partition {char}".format(char=first_char)
        schema_editor.execute(
            sql, ['{first_char}%'.format(first_char=first_char)])


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0018_allow_null_process_date'),
    ]

    operations = [
        migrations.RunPython(partition_address_table),
    ]
