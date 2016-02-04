# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0017_allow_null_entry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='process_date',
            field=models.DateField(null=True),
        ),
    ]
