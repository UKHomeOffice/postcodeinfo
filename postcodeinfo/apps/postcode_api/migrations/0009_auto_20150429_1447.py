# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0008_auto_20150427_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='etag',
            field=models.CharField(max_length=2048, null=True, db_index=True),
            preserve_default=True,
        ),
    ]
