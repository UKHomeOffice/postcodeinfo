# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0011_auto_20150702_1812'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('gss_code', models.CharField(max_length=9, serialize=False, primary_key=True, db_index=True)),
                ('name', models.CharField(max_length=128, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='postcodegsscode',
            name='country_gss_code',
            field=models.CharField(max_length=9, null=True, db_index=True),
        ),
    ]
