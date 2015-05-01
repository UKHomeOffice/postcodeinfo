# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0006_download'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='state',
            field=models.CharField(max_length=16, db_index=True),
            preserve_default=True,
        ),
    ]
