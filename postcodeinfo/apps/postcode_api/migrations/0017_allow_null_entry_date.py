# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0015_add_ni_local_authorities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='entry_date',
            field=models.DateField(null=True),
        ),
    ]
