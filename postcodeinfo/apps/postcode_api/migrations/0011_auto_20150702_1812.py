# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0010_auto_20150601_1513'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='address',
            index_together=set([('postcode_index', 'uprn')]),
        ),
    ]
