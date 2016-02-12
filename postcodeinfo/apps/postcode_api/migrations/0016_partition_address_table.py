# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string
import time

from django.contrib.gis.geos import Point
from django.db import migrations

from postcode_api.models import Address


def partition_address_table(apps, schema_editor):
    Address.architect.partition.get_partition().prepare()

    # the partition tables are only lazily created on-demand, so let's
    # aggressively pre-create them here by inserting & deleting an address
    # with each possible prefix
    dummy_date = time.strftime("%Y-%m-%d")
    all_possible_prefixes = string.ascii_lowercase + string.digits
    for first_char in all_possible_prefixes:
        tmp_address = Address.objects.create(postcode_index=first_char*6,
                                             point=Point(123, 123),
                                             rpc=012345,
                                             uprn=1234567890,
                                             start_date=dummy_date,
                                             last_update_date=dummy_date,
                                             entry_date=dummy_date,
                                             process_date=dummy_date
                                             )
        tmp_address.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0015_add_ni_local_authorities'),
    ]

    operations = [
        migrations.RunPython(partition_address_table),
    ]
