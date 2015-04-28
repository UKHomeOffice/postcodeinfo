# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0007_auto_20150427_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='last_modified',
            field=models.DateTimeField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='download',
            name='last_state_change',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
