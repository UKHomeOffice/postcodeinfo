# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0005_auto_20150417_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=2048, db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('etag', models.CharField(max_length=2048, db_index=True)),
                ('local_filepath', models.CharField(max_length=2048, db_index=True)),
                ('state', models.CharField(max_length=8, db_index=True)),
                ('last_state_change', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
