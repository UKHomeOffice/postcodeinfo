# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0018_allow_null_process_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='CacheVersion',
            fields=[
                ('last_addressbase_file', models.CharField(
                    max_length=128, serialize=False,
                    primary_key=False, db_index=True)),
                ('timestamp', models.DateTimeField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
