# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0002_address_postcode_area'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE postcode_api_address"
            "SET postcode_area = "
            "lower(split_part(postcode, ' ', 1));")
    ]
