# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0021_cache_version'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Download',
        ),
        migrations.AlterField(
            model_name='address',
            name='last_update_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='start_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='cacheversion',
            name='last_addressbase_file',
            field=models.CharField(max_length=128, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='cacheversion',
            name='timestamp',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
