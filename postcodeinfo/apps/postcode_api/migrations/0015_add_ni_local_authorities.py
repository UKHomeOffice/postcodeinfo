# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from os.path import dirname, join

from django.db import migrations

from postcode_api.models import LocalAuthority


def create_ni_local_authorities(apps, schema_editor):
    data_file = join(dirname(__file__), '../data/ni_local_authorities.csv')
    with open(data_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            local_authority, created = LocalAuthority.objects.get_or_create(
                gss_code=row['LGDCode'])
            local_authority.name = row['LGDNAME']
            local_authority.save()


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0014_reimport_nspl_to_pick_up_country_codes'),
    ]

    operations = [
        migrations.RunPython(create_ni_local_authorities),
    ]
